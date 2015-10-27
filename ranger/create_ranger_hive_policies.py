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
import logging
from collections import defaultdict

logging.getLogger().setLevel(logging.DEBUG)

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


def create_policies(policy_file, dry_run=False):

    policies = {}
    
    with open(policy_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        current_policy = None

        for row in reader:
            if row['Policy name'].startswith('#'):
                continue
            
            if row['Policy name'] not in policies and row['Policy name']:
                current_policy = policy_template.copy()
                policies[row['Policy name']] = current_policy
                current_policy['policyName'] = row['Policy name']
                current_policy['databases'] =  row['Resource']
                current_policy['description'] = 'CLU policy for %s' % row['Resource']
                current_policy['permMapList'] = [ {
                    'groupList': [row['AD groups']],
                    'permList': []
                }]

                if row['Select']: current_policy['permMapList'][0]['permList'].append('SELECT')
                if row['ALL']: current_policy['permMapList'][0]['permList'].append('ALL')

            else:
                current_policy['permMapList'].append({
                    'groupList': [row['AD groups']],
                    'permList': []
                })

                if row['Select']: current_policy['permMapList'][1]['permList'].append('Select')
                if row['ALL']: current_policy['permMapList'][1]['permList'].append('ALL')
    
    if dry_run:
        logging.debug('%s policies to be created' % len(policies))
        for name, policy in policies.iteritems():
            print name, policy['description'], policy['databases']
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
