#!/usr/bin/env python
"""
Small helper to create/update ranger policies from raw JSON policies (Hive)
"""

import json
import sys
import logging
import requests
import glob
from os.path import join as pjoin

logger = logging.getLogger(__name__)

ranger_host = 'localhost'
ranger_port = 6080
ranger_api = 'http://%s:%s/service/public/v2/api' % (ranger_host, ranger_port)
ranger_user = 'admin'
ranger_password = 'admin'
service_name = 'hive'

def check_service(service_name):
    """Check the existence of the service
    """
    headers = {
        'Content-Type': 'application/json'
    }
    r = requests.get('%s/service?serviceName=%s' % (ranger_api, service_name), auth=(ranger_user, ranger_password), headers=headers)

    if r.status_code != 200: logger.error(r.content)

    r.raise_for_status()

    data = r.json()

    if len(data) == 0:
        raise RuntimeError('Service not found')
    elif len(data) > 1:
        raise RuntimeError('More than one service found for %s' % service_name)

    return data[0]['id']

def get_policy(policy_name):
    """Retrieve the policy definition
    """
    headers = {
        'Content-Type': 'application/json'
    }
    r = requests.get('%s/service/%s/policy?policyName=%s' % (ranger_api, service_name, policy_name), auth=(ranger_user, ranger_password), headers=headers)

    if r.status_code != 200: logger.error(r.content)

    r.raise_for_status()

    data = r.json()

    if len(data) > 1:
        raise RuntimeError('More than one policy found for %s' % policy_name)

    elif len(data) == 0:
        return None

    else:
        return data[0]

def update_policy(policy_id, policy):
    """Update the policy
    """
    logger.info('Updating policy %s', policy_id)
    headers = {
        'Content-Type': 'application/json'
    }
    policy['service'] = service_name
    r = requests.put('%s/policy/%s' % (ranger_api, policy_id), headers=headers, auth=(ranger_user, ranger_password), data=json.dumps(policy))

    if r.status_code != 200: logger.error(r.content)

    r.raise_for_status()


def create_policy(service_name, data):
    """Create the policy
    """
    logger.info('Creating new policy %s', data['name'])
    headers = {
        'Content-Type': 'application/json'
    }
    data['service'] = service_name
    r = requests.post('%s/policy' %  (ranger_api,), headers=headers, auth=(ranger_user, ranger_password), data=json.dumps(data))

    if r.status_code != 200: logger.error(r.content)

    r.raise_for_status()


def create_or_update_all_policies(policy_dir):
    """Look for all policies in a directory (json) and attempt to update or create if they are not yet defined
    """
    for filename in glob.glob(pjoin(policy_dir, '*.json')):
        with open(filename) as f:
            new_policy = json.load(f)
            existing_policy = get_policy(new_policy['name'])
            if existing_policy:
                update_policy(existing_policy['id'], new_policy)
            else:
                create_policy(service_name, new_policy)


if __name__ == '__main__':
    from optparse import OptionParser

    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
    logger.setLevel(logging.DEBUG)

    parser = OptionParser()

    options, args = parser.parse_args()

    create_or_update_all_policies('hive-policies')
