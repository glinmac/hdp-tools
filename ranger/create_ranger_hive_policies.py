#!/usr/bin/env python
"""
Input file is  a CSV:
Policy name, Resource, AD groups, Select, ALL, Comment
"""

import csv
import json
from httplib import HTTPConnection
from base64 import b64encode
import sys

ranger_host = '<HOST>'
ranger_port = 6080
policy_api = '/service/public/api/policy'
ranger_user = '<USERNAME>'
ranger_password = '<PASSWORD>'
repository_name = '<REPONAME>'
description_template = 'Policy for %s'

policy_template = {
    'policyName': '',
    'databases': '',
    'tables': '*',
    'columns': '*',
    'udfs': '',
    'description': '',
    'repositoryName': repository_name,
    'repositoryType': 'hive',
    'tableType': 'inclusion',
    'columnType': 'inclusion',
    'isEnabled': True,
    'isAuditEnabled': True,
    'permMapList': []
}

def create_policy(data):
    conn = HTTPConnection(host=ranger_host, port=ranger_port)
    headers = { 
        'Authorization' : 'Basic %s' % b64encode('%s:%s' % (ranger_user, ranger_password)),
        'Content-Type': 'application/json'
    }
    conn.request('POST', policy_api, headers=headers, body=json.dumps(data))
    response = conn.getresponse()
    if response.status != 200:
       print 'Error creating policy %s: %s' % (data['policyName'], data)
       print response.read()
    else:
       print 'Policy %s created' % data['policyName']


with open(sys.argv[1]) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    policy = policy_template

    for row in reader:
        if row['Policy name']:
            policy['policyName'] = row['Policy name']
            policy['databases'] =  row['Resource']
            policy['description'] = description % row['Resource']
            policy['permMapList'] = [ {
                'groupList': [row['AD groups']],
                'permList': []
            }]

            if row['Select']: policy['permMapList'][0]['permList'].append('SELECT')
            if row['ALL']: policy['permMapList'][0]['permList'].append('ALL')

        else:
            policy['permMapList'].append({
                'groupList': [row['AD groups']],
                'permList': []
            })

            if row['Select']: policy['permMapList'][1]['permList'].append('Select')
            if row['ALL']: policy['permMapList'][1]['permList'].append('ALL')

            create_policy(policy)
            
            policy = policy_template
