#!/usr/bin/env python
"""
Create some specific widgets and add them to a layout.
Specific configuration elements are provided in localparams.py file
"""
import csv
import json
from httplib import HTTPConnection
from base64 import b64encode
import sys
from localparams import *
from urllib import quote
import logging

logger = logging.getLogger(__name__)

class AmbariClient(object):
    """Quick Ambari wrapper
    """
    def __init__(self, host, port, user, password):
        self.conn = HTTPConnection(host=host, port=port)
        self.get_headers = {
            'Authorization' : 'Basic %s' % b64encode('%s:%s' % (user, password)),
            'Content-Type': 'application/json',
            'X-Requested-By': 'ambari'
        }
        self.write_headers = {
            'Authorization' : 'Basic %s' % b64encode('%s:%s' % (user, password)),
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-By': 'ambari'
        }

    def get(self, endpoint):
        """GET with JSON result
        """
        self.conn.request('GET', endpoint, headers=self.get_headers)
        response = self.conn.getresponse()
        if response.status not in xrange(200, 207):
            logger.debug('GET %s' % endpoint)
            logger.debug(response.read())
            raise RuntimeError('Error connecting to %s, status=%s' % (endpoint, response.status))
        content = response.read()
        if content:
            return json.loads(content)
        else:
            return None

    def _write(self, method, endpoint, data):
        self.conn.request(method, endpoint, headers=self.write_headers, body=data)
        response = self.conn.getresponse()
        if response.status not in xrange(200, 207):
            logger.debug('POST %s' % endpoint)
            logger.debug(response.read())
            raise RuntimeError('Error connecting to %s, status=%s' % (endpoint, response.status))
        content = response.read()
        if content:
            return json.loads(content)
        else:
            return None

    def put(self, endpoint, data):
        """PUT request
        """
        self._write('PUT', endpoint, data)

    def post(self, endpoint, data):
        """POST request
        """
        self._write('POST', endpoint, data)

client = AmbariClient(ambari_host, ambari_port, ambari_user, ambari_password)

def list_widgets():
    """List all widgets
    """
    data = client.get('%s/widgets' % ambari_api)
    return data['items']

def list_layout_widgets(layout_name):
    """List all widgets in a given layout
    """
    data = client.get('%s/widget_layouts?WidgetLayoutInfo/layout_name=%s' % (ambari_api, layout_name))
    return data['items'][0]['WidgetLayoutInfo']

def create_widget(name, widget_data):
    """Create a given widget
    """
    data = client.post('%s/widgets' % ambari_api, json.dumps(widget_data))
    return data['resources'][0]['WidgetInfo']['id']

def update_widget_layout(layout_data):
    """Update a layout with a new def
    """
    data = client.put('%s/widget_layouts/%s' % (ambari_api,
        layout_data['WidgetLayoutInfo']['id']),
        json.dumps(layout_data))

if __name__ == '__main__':
    from optparse import OptionParser
    import os.path

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

    parser = OptionParser()

    options, args = parser.parse_args()

    # Get all widgets
    widgets = {}
    for w in list_widgets():
        widgets[w['WidgetInfo']['widget_name']] = w['WidgetInfo']['id']

    # Get all widgets for the given layout
    layout_widgets = {}
    layout_data = list_layout_widgets(widget_layout)
    for w in layout_data['widgets']:
        layout_widgets[w['WidgetInfo']['widget_name']] = w['WidgetInfo']['id']

    new_ids = []

    # Create all widgets
    for ref_name,w in new_widgets.iteritems():
        try:
            new_id = None
            if w['WidgetInfo']['widget_name'] not in widgets:
                new_id = create_widget(w['WidgetInfo']['widget_name'], w)
                logger.info('Widget %s created (id=%s)' % (w['WidgetInfo']['widget_name'], new_id))
            else:
                logger.info('Widget %s already present' % w['WidgetInfo']['widget_name'])

            if w['WidgetInfo']['widget_name'] not in layout_widgets:
                if new_id is None:
                    new_id = widgets[w['WidgetInfo']['widget_name']]
                new_ids.append(new_id)

            else:
                logger.info('Widget %s already part of layout %s' % (w['WidgetInfo']['widget_name'], widget_layout))
        except Exception as ex:
            logger.error(ex)

    # add widgets to layout
    if new_ids:
        updated_layout_data = {
            'WidgetLayoutInfo': {
                'display_name': layout_data['display_name'],
                'id': layout_data['id'],
                'layout_name': layout_data['layout_name'],
                'scope': layout_data['scope'],
                'section_name': layout_data['section_name'],
                'widgets': [ {'id':w['WidgetInfo']['id']} for w in layout_data['widgets'] if w['WidgetInfo']['widget_name'] not in new_widgets]
            }
        }
        updated_layout_data['WidgetLayoutInfo']['widgets'].extend([{'id': n} for n in new_ids])
        update_widget_layout(updated_layout_data)
        logger.info('Widgets added to layout %s' % widget_layout)
    else:
        logger.info('No widget added to layout %s' % widget_layout)
