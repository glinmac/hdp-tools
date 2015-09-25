#!/usr/bin/env python
import csv
import sys
import subprocess

create_key_cmd = 'hadoop key create %(key)s'
create_path_cmd = 'hdfs dfs -mkdir %(path)s'
create_ez_cmd = 'hdfs crypto -createZone -path %(path)s -keyName %(key)s'

with open(sys.argv[1]) as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for row in r:
        if '/' in row[1]:
            d = { 'path': row[1], 'key': row[2]}
            try:
                subprocess.call((create_key_cmd % d).split(' '))
                subprocess.call((create_path_cmd %d).split(' '))
                subprocess.call((create_ez_cmd % d).split(' '))
                print 'Success creation EZ (%(key)s, %(path)s)' % d
            except Exception as ex:
                print 'Error creating EZ (%(key)s, %(path)s)' % d
                print ex
