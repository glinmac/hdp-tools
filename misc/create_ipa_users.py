#!/usr/bin/env python
"""
Small script to automate user/groups creation and keytab retrieval using FreeIPA

Users file format: a CSV file with at least 2 columns named 'Name', 'Description',

Name,Description,...
username,account for username,...

Groups file format: a CSV file with at least 2 columns named 'Name', 'Description'

Name,Description,...
group1,unix group for group1,...

Membership file format: a CSV file with a least 2 columns names 'Group', 'Member'

Group,Member,...
group1,username,...
group2,username,...


Tested on redhat 6.4/python2.6/freeipa 3.0.0

"""
import csv
import sys
import subprocess
from tempfile import mkstemp
import os
import re
import logging
from collections import defaultdict

logging.getLogger().setLevel(logging.DEBUG)

# some global variables to target the systems
IPA_SERVER="<YOUR_IPASERVER>"
REALM="<YOUR_REAML>"
IPA_PASSWORD="<MASTER_IPA_PASSWORD>"
INIT_PASSWORD="<INITIAL_PASSWORD_FOR_USER>"
DEFAULT_PASSWORD="<DEFAULT_PASSWORD_FOR_USER>"
BASE_GROUPS=[
    'DEFAULT_GROUP1',
    'DEFAULT_GROUP2'
]

# Template for commands
check_user_cmd = "ipa user-find --login %(username)s"
check_group_cmd = "ipa group-find --group-name %(groupname)s"
get_user_dn_cmd = "ipa user-find --login=%(username)s --all" 
create_user_cmd = "ipa user-add %(username)s --first=%(first)s --last=%(last)s --password"
reset_krb_expiration = "ldapmodify -D 'cn=directory manager' -w %(ipa_password)s -f %(path)s"
create_keytab_cmd = "ipa-getkeytab -s %(ipa_server)s -p %(username)s@%(realm)s -k %(path_prefix)s/.%(username)s-headless.keytab -P"
add_group_cmd = "ipa group-add-member %(group)s --users=%(user)s"
create_group_cmd = "ipa group-add %(group)s --desc=\"%(description)s\""

def user_exists(username):
    return subprocess.call((check_user_cmd % {'username': username}).split(), stdout=subprocess.PIPE) == 0

def group_exists(groupname):
    return subprocess.call((check_group_cmd % {'groupname': groupname}).split(), stdout=subprocess.PIPE) == 0

def get_user_dn(username):
    p = subprocess.Popen((get_user_dn_cmd % {'username': username}).split(), stdout=subprocess.PIPE)
    out, _ = p.communicate()
    for line in out.split('\n'):
        m = re.search('\s*dn:\s*(\S+)', line)
        if m:
            return m.group(1)
    return None
    
def change_krb_expiration(username):
    temp_f, temp_path = mkstemp()
    
    try:
        user_dn = get_user_dn(username)
        if user_dn is None:
            raise RuntimeError('Empty user dn')
        with open(temp_path, 'w') as f:
            f.write('dn: %s\n' % user_dn)
            f.write('changetype: modify\n')
            f.write('replace: krbpasswordexpiration\n')
            f.write('krbpasswordexpiration: 20190101000000Z\n')
        subprocess.check_call(reset_krb_expiration % {'path': temp_path, 'ipa_password': IPA_PASSWORD}, shell=True, stdout=subprocess.PIPE)

    finally:
        os.unlink(temp_path)
    
def create_user(data):
    logging.debug('Creating user %s' % data['username'])
    p = subprocess.Popen((create_user_cmd % data).split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate(input='%(password)s\n%(password)s\n' % {'password': INIT_PASSWORD})

def create_keytab(data):
    logging.debug('Creating keytab')
    p = subprocess.Popen((create_keytab_cmd % data).split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate(input='%(password)s\n%(password)s\n' % {'password': DEFAULT_PASSWORD})

def add_group(username, groupname):
    logging.debug('Adding %s to group %s' % (username, groupname))
    p = subprocess.Popen((add_group_cmd % {'user': username, 'group': groupname}).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    out, err = p.communicate()
    if p.returncode:
        if 'entry is already a member' in out:
            logging.debug('User %s already a member of %s' % (username, groupname))
        else:
            raise RuntimeError(out)
    
def create_group(groupname, description=None):
    logging.debug('Creating group %s' % groupname)
    subprocess.check_call(create_group_cmd % { 'group': groupname, 'description': description if description else groupname}, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def process_users(users_file, keytab_path):

    with open(users_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Name'] == '#':
                continue
            d = {
                'username': row['Name'],
                'description': row['Description'],
                'first': row['Name'],
                'last': row['Name'],
                'realm': REALM,
                'ipa_server': IPA_SERVER,
                'path_prefix': keytab_path
            }

            if not user_exists(d['username']):
                create_user(d)
                # When a user is created in IPA, his password autoexpires.
                # Need to explicitly login or set the expiration to a later date so that the keytab
                # can be retrieved and used later
                change_krb_expiration(d['username'])                    
                create_keytab(d)
                for g in BASE_GROUPS:
                    add_group(d['username'], g)
            else:
                logging.debug('User %s already exists' % d['username'])


def process_groups(group_file):
    with open(group_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Name'] == '#':
                continue
            if not group_exists(row['Name']):
                create_group(row['Name'], row['Description'])
                    
def process_membership(membership_file):
    with open(membership_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Group'][0] == '#':
                continue
            if not group_exists(row['Group']):
                create_group(row['Group'])
            add_group(row['Member'], row['Group'])

def validate_users(users_file):
    users = []
    with open(users_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Name'] == '#':
                continue
            if row['Name'] not in users:
                users.append(row['Name'])
            else:
                logging.error('Duplicate user %s in user file %s' % (row['Name'], users_file))
    return users

def validate_groups(groups_file):
    groups = []
    with open(groups_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Name'] == '#':
                continue
            if row['Name'] not in groups:
                groups.append(row['Name'])
            else:
                logging.error('Duplicate user %s in group file %s' % (row['Name'], groups_file))
    return groups

def validate_membership(membership_file):
    membership = defaultdict(list)
    with open(membership_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Group'] == '#':
                continue
            if row['Group'] in membership:
                if row['Member'] not in membership[row['Group']]:
                    membership[row['Group']].append(row['Member'])
                else:
                    logging.error('Duplicate membership user=%s, group=%s' % (row['Member'], row['Group']))
            else:
                membership[row['Group']].append(row['Member'])
    return membership


if __name__ == '__main__':
    from optparse import OptionParser
    import os.path
    
    parser = OptionParser()
    parser.add_option('--users', dest='users',
                      help='List of users', metavar='FILE')
    parser.add_option('--membership', dest='membership',
                      help='User/Group membership', metavar='FILE')
    parser.add_option('--keytab-path', dest='keytab_path',
                      help='Path to save keytabs', metavar='FILE')
    parser.add_option('--groups', dest='groups',
                      help='List of groups', metavar='FILE')
    parser.add_option('--validate', dest='validate', action='store_true',
                      help='Validate input files')
    
    options, args = parser.parse_args()

    if options.validate:
        users, groups, membership = [], [], defaultdict(list)
        if options.users:
            users = validate_users(options.users)
        if options.groups:
            groups = validate_groups(options.groups)
        if options.membership:
            membership = validate_membership(options.membership)

        if users and groups and membership:
            for group, val in membership.iteritems():
                if group not in groups:
                    logging.warning('group %s not in group file' % group)
                for user in val:
                    if user not in users:
                        logging.warning('user %s not in user file' % user)

        logging.info('%d users going to be created' % len(users))
        logging.info('%d groups going to be created' % len(groups))
        logging.info('%d groups will have members updated' % len(membership.keys()))


    else:
        if options.users:
            if not options.keytab_path:
                raise RuntimeError('keytab path not specified (--keytab-path)')
            if not os.path.exists(options.keytab_path):
                os.makedirs(options.keytab_path)
            elif not os.path.isdir(options.keytab_path):
                raise RuntimeError('keytab path already exists and is not a directory')

            process_users(options.users, options.keytab_path)

        if options.groups:
            process_groups(options.groups)

        if options.membership:
            process_membership(options.membership)

        
