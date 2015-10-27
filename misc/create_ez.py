#!/usr/bin/env python
"""
Create some encryption zones

Expected format for CSV:

Zone name,Path,Keyname,....

"""

import csv
import sys
import subprocess
import logging

logging.getLogger().setLevel(logging.DEBUG)

check_path_exists_cmd = 'hdfs dfs -test -e %(path)s'
check_path_is_dir_cmd = 'hdfs dfs -test -d %(path)s'   
create_key_cmd = 'hadoop key create %(key)s'
create_path_cmd = 'hdfs dfs -mkdir %(path)s'
create_ez_cmd = 'hdfs crypto -createZone -path %(path)s -keyName %(key)s'
get_zones_cmd = 'hdfs crypto -listZones'
get_keys_cmd = 'hadoop key list'

def get_keys():
    keys = []
    p = subprocess.Popen(get_keys_cmd.split(), stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        keyname = line.strip()
        if len(keyname):
            keys.append(keyname)
     
    return keys
    
def get_zones():
    zones = {}
    p = subprocess.Popen(get_zones_cmd.split(), stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        comp = [ el for el in line.split(' ') if el ]
        if len(comp):
            zones[comp[0]] = comp[1]
    return zones
        
def hdfs_path_exists(path):
    return subprocess.call((check_path_exists_cmd % {'path':path}).split(' ')) == 0

def hdfs_path_is_dir(path):
    return subprocess.call((check_path_is_dir_cmd % {'path':path}).split(' ')) == 0

def create_hdfs_dir(path):
    subprocess.check_call((create_path_cmd % {'path': path}).split(' '))

def create_key(name):
    subprocess.call((create_key_cmd % {'key':name}).split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def create_encryption_zone(path, keyname):
    subprocess.check_call((create_ez_cmd % {'path': path, 'key':keyname}).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def create_ez(ez_file, dry_run=False):
    
    existing_zones, existing_keys = get_zones(), get_keys()
    
    zones = {}

    # List all encryption zones to be created
    with open(ez_file) as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:
            if row['Zone name'].startswith('#'):
                continue
            
            if row['Path']:
                zones[row['Zone name']] = { 'path': row['Path'], 'key': row['Keyname']}
                
    if dry_run:
        # dry run, just some basic checks and info
        logging.info('%s encryption zones to be created' % len(zones))
        for name, zone in zones.iteritems():
            if not hdfs_path_exists(zone['path']):
                logging.debug('%s will be created on HDFS' % zone['path'])
            if zone['key'] in existing_keys:
                logging.warn('%s: key already created' % zone['key'])
            if zone['path'] in existing_zones:
                logging.warn('%s already an EZ with key %s' % (zone['path'], existing_zones[zone['path']]))
    else:
    
        # Creation the zones
        for name, zone in zones.iteritems():
            try:
                # Skip if EZ already exists
                if zone['path'] in existing_zones:
                    logging.warn('%s already an EZ with key %s - skipping' % (zone['path'], existing_zones[zone['path']]))
                    continue
                logging.debug('Creating EZ (%(key)s, %(path)s)' % zone)
                
                # Create key if needed
                if zone['key'] in existing_zones:
                    logging.warn('%s key already present, not created' % zone['key'])
                else:
                    create_key(zone['key'])
                    
                # Create path if needed
                if not hdfs_path_exists(zone['path']):
                    create_hdfs_dir(zone['path'])
                if not hdfs_path_is_dir(zone['path']):
                    raise RuntimeError('%s is not a directory' % zone['path'])
                
                # at last, create the EZ
                create_encryption_zone(zone['path'], zone['key'])
                
                logging.info('Success creation EZ (%(key)s, %(path)s)' % zone)
            except Exception as ex:
                logging.error('Error creating EZ (%(key)s, %(path)s)' % zone)
                logging.debug(ex)

if __name__ == '__main__':
    from optparse import OptionParser
    import os.path
    
    parser = OptionParser()
    
    parser.add_option('--dry-run', dest='dry_run', action='store_true', default=False,
                      help='Dry run')
    options, args = parser.parse_args()
    
    create_ez(args[0], dry_run=options.dry_run)
