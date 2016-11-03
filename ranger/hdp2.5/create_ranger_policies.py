#!/usr/bin/env python
"""
Small helper to create/update ranger policies from raw JSON policies
"""

import json
import sys
import logging
import requests
import glob
from os.path import join as pjoin

logger = logging.getLogger(__name__)


class RangerApi():

    def __init__(self, user='admin', password='admin', host='localhost', port=6080, service='hadoop'):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.base_url = 'http://%s:%s/service/public/v2/api' % (self.host, self.port)
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.service = service


    def check_service(self):
        """Check the existence of the service
        """
        logger.info('Checking service %s', self.service)

        r = requests.get('%s/service?serviceName=%s' % (self.base_url, self.service),
                         auth=(self.user, self.password),
                         headers=self.headers)

        if r.status_code != 200: logger.error(r.content)

        r.raise_for_status()

        data = r.json()

        if len(data) == 0:
            raise RuntimeError('Service not found')
        elif len(data) > 1:
            raise RuntimeError('More than one service found for %s' % self.service)

        return data[0]['id']


    def get_policy(self, policy_name):
        """Retrieve the policy definition
        """
        logger.info('Fetching policy %s', policy_name)

        r = requests.get('%s/service/%s/policy?policyName=%s' % (self.base_url, self.service, policy_name),
                         auth=(self.user, self.password),
                         headers=self.headers)

        if r.status_code != 200: logger.error(r.content)

        r.raise_for_status()

        data = r.json()

        if len(data) > 1:
            raise RuntimeError('More than one policy found for %s.%s' % (self.service, policy_name))

        elif len(data) == 0:
            return None

        else:
            return data[0]


    def update_policy(self, policy_id, policy):
        """Update the policy
        """
        logger.info('Updating policy %s (id=%s)', policy['name'], policy_id)

        r = requests.put('%s/policy/%s' % (self.base_url, policy_id),
                         headers=self.headers,
                         auth=(self.user, self.password),
                         data=json.dumps(policy))

        if r.status_code != 200: logger.error(r.content)

        r.raise_for_status()


    def create_policy(self, policy):
        """Create the policy
        """
        logger.info('Creating new policy %s', policy['name'])

        r = requests.post('%s/policy' %  (self.base_url,),
                          headers=self.headers,
                          auth=(self.user, self.password),
                          data=json.dumps(policy))

        if r.status_code != 200: logger.error(r.content)

        r.raise_for_status()


    def create_or_update_all_policies(self, policy_dir):
        """Look for all policies in a directory (json) and attempt to update or
        create if they are not yet defined.
        """
        logger.info('Creating/updating policies in path %s', policy_dir)

        for filename in glob.glob(pjoin(policy_dir, '*.json')):
            with open(filename) as f:
                new_policy = json.load(f)
                existing_policy = self.get_policy(new_policy['name'])
                new_policy['service'] = self.service
                if existing_policy:
                    self.update_policy(existing_policy['id'], new_policy)
                else:
                    self.create_policy(new_policy)


if __name__ == '__main__':
    import argparse

    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='Create/Update Ranger Hive policies')
    parser.add_argument('--user', dest='user', default='admin',
                        help='User to connect to the Ranger API')
    parser.add_argument('--password', dest='password', default='admin',
                        help='Password to connect to the Ranger API')
    parser.add_argument('--host', dest='host', default='localhost',
                        help='Host to connect to the Ranger API')
    parser.add_argument('--port', dest='port', type=int, default=6080,
                        help='Port to connect to the Ranger API')
    parser.add_argument('--service', dest='service', default='hadoop',
                        help='The name of the Ranger service to use to create policies')


    args = parser.parse_args()

    api = RangerApi(user=args.user,
                    password=args.password,
                    host=args.host,
                    port=args.port,
                    service=args.service)

    api.create_or_update_all_policies('hive-policies')

