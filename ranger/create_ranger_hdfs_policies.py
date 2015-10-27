#!/usr/bin/env python
"""
Input file is  a CSV:
Policy name, Resource path, AD groups, Read, Write, Execute, Comment
"""

import csv
import json
from httplib import HTTPConnection
from base64 import b64encode
import sys
import logging
from collections import defaultdict

logging.getLogger().setLevel(logging.DEBUG)

ranger_host = '<HOST>'
ranger_port = 6080
policy_api = '/service/public/api/policy'
ranger_user = '<USER>'
ranger_password = '<PASSWORD>'
repository_name = '<REPONAME>'
description_template = 'Policy for %s'
policy_template = {
    'policyName': '',
    'resourceName': '',
    'description': '',
    'repositoryName': repository_name,
    'repositoryType': 'hdfs',
    'isEnabled': True,
    'isRecursive': True,
    'isAuditEnabled': True,
    'permMapList': []
}


policy_template = {
    'policyName': '',
    'resourceName': '',
    'description': '',
    'repositoryName': repository_name,
    'repositoryType': 'hdfs',
    'isEnabled': True,
    'isRecursive': True,
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
       logging.error('Error creating policy %s: %s' % (data['policyName'], data))
       logging.debug(response.read())
    else:
       logging.info('Policy %s created' % data['policyName'])

def create_policies(policy_file, dry_run=False):

    policies = {}
    
    # read all policies
    with open(policy_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        current_policy_name = None
        
        for row in reader:
            
            if row['Policy name'].startswith('#'):
                continue
                
            if row['Policy name'] not in policies and row['Policy name']:
                current_policy_name = row['Policy name']
                policies[row['Policy name']] = policy_template.copy()
                policies[row['Policy name']]['policyName'] = row['Policy name']
                policies[row['Policy name']]['resourceName'] = row['Resource path']
                policies[row['Policy name']]['description'] = description_template % row['Resource path']
                policies[row['Policy name']]['permMapList'] = [ {
                 'groupList': [row['AD groups']],
                 'permList': []
                }]

                if row['Read']: policies[row['Policy name']]['permMapList'][0]['permList'].append('Read')
                if row['Write']: policies[row['Policy name']]['permMapList'][0]['permList'].append('Write')
                if row['Execute']: policies[row['Policy name']]['permMapList'][0]['permList'].append('Execute')

            else:
                 policies[current_policy_name]['permMapList'].append({
                     'groupList': [row['AD groups']],
                     'permList': []
                 })
                 
                 if row['Read']: policies[current_policy_name]['permMapList'][1]['permList'].append('Read')
                 if row['Write']: policies[current_policy_name]['permMapList'][1]['permList'].append('Write')
                 if row['Execute']: policies[current_policy_name]['permMapList'][1]['permList'].append('Execute')
                 
    if dry_run:
        logging.debug('%s policies to be created' % len(policies))
        for name, policy in policies.iteritems():
            print name, policy['description'], policy['resourceName']
    else:
        for name, policy in policies.iteritems():
            create_policy(policy)             


if __name__ == '__main__':
    from optparse import OptionParser
    import os.path
    
    parser = OptionParser()
    parser.add_option('--dry-run', dest='dry_run', action='store_true', default=False,
                      help='Dry run')

    options, args = parser.parse_args()
    
    create_policies(args[0], dry_run=options.dry_run)
