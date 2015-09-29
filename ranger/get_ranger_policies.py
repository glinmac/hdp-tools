#!/usr/bin/env python
"""
Retrieve Ranger policies
"""

import csv
import json
from httplib import HTTPConnection
from base64 import b64encode
import sys

ranger_host = '<HOSTNAME>'
ranger_port = 6080
policy_api = '/service/public/api/policy'
ranger_user = '<USER>'
ranger_password = '<PASSWORD>'

def get_policies():
    conn = HTTPConnection(host=ranger_host, port=ranger_port)
    headers = {
        'Authorization' : 'Basic %s' % b64encode('%s:%s' % (ranger_user, ranger_password)),
        'Content-Type': 'application/json'
    }
    conn.request('GET', policy_api, headers=headers)
    response = conn.getresponse()
    if response.status != 200:
       print 'Error retrieving policies'
       print response.read()
       raise RuntimeError('HTTP code:%s, Reason: %s' % (response.status, response.msg))

    return json.loads(response.read())


if __name__ == '__main__':
    res = get_policies()
    # properties of the reply from ranger
    # PgeSize, vXPolicies, resultSize, queryTimeMS, totalCount

    print '%s policies available' % res['totalCount']

    for p in res['vXPolicies']:
       print p['policyName'], p['repositoryType'], p['repositoryName'], p['resourceName']
