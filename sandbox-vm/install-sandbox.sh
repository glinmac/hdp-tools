#!/bin/sh
##
## Script for single node setup Ambari / HDP
##

set -e

# Some variables
AMBARI_USER=admin
AMBARI_PASSWORD=admin
CLUSTER_NAME=sandbox
AMBARI_API=http://127.0.0.1:8080/api/v1/clusters/$CLUSTER_NAME
HOST_API=http://127.0.0.1:8080/api/v1/hosts
BLUEPRINT_API=http://127.0.0.1:8080/api/v1/blueprints
RANGER_API=http://127.0.0.1:6080/service/public/api
RANGER_USER=admin
RANGER_PASSWORD=admin
BLUEPRINT_NAME=hdp-singlenode-2.2

export JAVA_HOME=/usr/lib/jvm/jre-1.7.0

SCRIPT_DIR=$(pwd)

# Define HDP and Ambari repo
echo "Installing Yum repo..."
cp resources/hdp.repo /etc/yum.repos.d
cp resources/ambari.repo /etc/yum.repos.d

# Install dependencies
echo "Installing dependencies..."
yum install -y ntp java-1.7.0-openjdk
chkconfig ntpd on
service ntpd restart

# Install Ambari agent / server
echo "Installing Ambari..."
yum install -y ambari-agent ambari-server
setenforce 0
ambari-server setup --java-home=$JAVA_HOME -s
service ambari-agent start
service ambari-server start

# Wait for server to be started
echo "Waiting for agent to register..."
sleep 120

# Wait for agent to register
REGISTERED=0
while [ "$REGISTERED" -eq 0 ]; do
        cnt=$(curl -s -u $AMBARI_USER:$AMBARI_PASSWORD -H 'X-Requested-By: ambari' -X GET $HOST_API | python -c 'import json, sys; print len(json.load(sys.stdin)["items"])')
        if [ "$cnt" = "1" ]; then
            echo "Ambari Agent registered"
            REGISTERED=1
        else
            echo "Waiting for agent to register..."
            sleep 60
        fi
done

echo "Deploying blueprint..."
# Register blueprint
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i \
    -H 'X-Requested-By: ambari' \
    -X POST -d @resources/${BLUEPRINT_NAME}.json \
    $BLUEPRINT_API/${BLUEPRINT_NAME}

# Create cluster script
sed -e s/_FQDN_/$(hostname)/ resources/cluster-creation-template.json > cluster-creation.json

# Create cluster
curl -u $AMBARI_USER:$AMBARI_PASSWORD -s \
    -H 'X-Requested-By: ambari'\
    -X POST -d @cluster-creation.json  \
    $AMBARI_API

# Wait for completion
COMPLETED=0
while [ "$COMPLETED" -eq 0 ]; do
    status=$(curl -s -u $AMBARI_USER:$AMBARI_PASSWORD -H 'X-Requested-By: ambari' -X GET $AMBARI_API/requests/1?fields=Requests | python -c 'import json, sys; print json.load(sys.stdin)["Requests"]["request_status"]')
    if [ "$status" = "COMPLETED" ]; then
        echo "Cluster created"
        COMPLETED=1
    else
        echo "Waiting for cluster to be ready..."
        sleep 60
    fi
done;

# Install and configure ranger
echo "Installing Ranger ..."
yum install -y ranger-admin ranger-usersync ranger-hdfs-plugin ranger-hive-plugin ranger-knox-plugin ranger-hbase-plugin

# Start mysql
service mysqld start

# Get current HDP_VERSION
HDP_VERSION=$(hdp-select status ranger-admin | cut -d ' ' -f 3)

# Ranger-admin
cd /usr/hdp/$HDP_VERSION/ranger-admin
sh set_globals.sh
sed -i.bak \
    -e 's/^db_password=/db_password=password/' \
    -e 's/^audit_db_password=/audit_db_password=password/' \
    install.properties
sh setup.sh
service ranger-admin start

sleep 120

cd /usr/hdp/$HDP_VERSION/ranger-usersync
sed -i.bak \
    -e 's/^POLICY_MGR_URL =/POLICY_MGR_URL=http:\/\/127.0.0.1:6080/' \
    -e 's/^SYNC_SOURCE =/SYNC_SOURCE=unix/' \
    install.properties
sh set_globals.sh
sh setup.sh
service ranger-usersync start

# Ranger HDFS plugin
cd /usr/hdp/$HDP_VERSION/ranger-hdfs-plugin
sed -i.bak \
    -e 's/^POLICY_MGR_URL=/POLICY_MGR_URL=http:\/\/127.0.0.1:6080/' \
    -e "s/^REPOSITORY_NAME=/REPOSITORY_NAME=${CLUSTER_NAME}-hdfs/" \
    -e 's/^XAAUDIT.DB.HOSTNAME=/XAAUDIT.DB.HOSTNAME=localhost/' \
    -e 's/^XAAUDIT.DB.DATABASE_NAME=/XAAUDIT.DB.DATABASE_NAME=ranger_audit/' \
    -e 's/^XAAUDIT.DB.USER_NAME=/XAAUDIT.DB.USER_NAME=ranger_logger/' \
    -e 's/^XAAUDIT.DB.PASSWORD=/XAAUDIT.DB.PASSWORD=password/' \
    install.properties
sh enable-hdfs-plugin.sh

# Ranger HBase plugin
cd /usr/hdp/$HDP_VERSION/ranger-hbase-plugin
sed -i.bak \
    -e 's/^POLICY_MGR_URL=/POLICY_MGR_URL=http:\/\/127.0.0.1:6080/' \
    -e "s/^REPOSITORY_NAME=/REPOSITORY_NAME=${CLUSTER_NAME}-hbase/" \
    -e 's/^XAAUDIT.DB.HOSTNAME=/XAAUDIT.DB.HOSTNAME=localhost/' \
    -e 's/^XAAUDIT.DB.DATABASE_NAME=/XAAUDIT.DB.DATABASE_NAME=ranger_audit/' \
    -e 's/^XAAUDIT.DB.USER_NAME=/XAAUDIT.DB.USER_NAME=ranger_logger/' \
    -e 's/^XAAUDIT.DB.PASSWORD=/XAAUDIT.DB.PASSWORD=password/' \
    install.properties
sh enable-hbase-plugin.sh

# Ranger Hive plugin
cd /usr/hdp/$HDP_VERSION/ranger-hive-plugin
sed -i.bak \
    -e 's/^POLICY_MGR_URL=/POLICY_MGR_URL=http:\/\/127.0.0.1:6080/' \
    -e "s/^REPOSITORY_NAME=/REPOSITORY_NAME=${CLUSTER_NAME}-hive/" \
    -e 's/^XAAUDIT.DB.HOSTNAME=/XAAUDIT.DB.HOSTNAME=localhost/' \
    -e 's/^XAAUDIT.DB.DATABASE_NAME=/XAAUDIT.DB.DATABASE_NAME=ranger_audit/' \
    -e 's/^XAAUDIT.DB.USER_NAME=/XAAUDIT.DB.USER_NAME=ranger_logger/' \
    -e 's/^XAAUDIT.DB.PASSWORD=/XAAUDIT.DB.PASSWORD=password/' \
    install.properties
sh enable-hive-plugin.sh

# Ranger Knox plugin
cd /usr/hdp/$HDP_VERSION/ranger-knox-plugin
sed -i.bak \
    -e 's/^POLICY_MGR_URL=/POLICY_MGR_URL=http:\/\/127.0.0.1:6080/' \
    -e "s/^REPOSITORY_NAME=/REPOSITORY_NAME=${CLUSTER_NAME}-knox/" \
    -e 's/^XAAUDIT.DB.HOSTNAME=/XAAUDIT.DB.HOSTNAME=localhost/' \
    -e 's/^XAAUDIT.DB.DATABASE_NAME=/XAAUDIT.DB.DATABASE_NAME=ranger_audit/' \
    -e 's/^XAAUDIT.DB.USER_NAME=/XAAUDIT.DB.USER_NAME=ranger_logger/' \
    -e 's/^XAAUDIT.DB.PASSWORD=/XAAUDIT.DB.PASSWORD=password/' \
    install.properties
sh enable-knox-plugin.sh

cd ${SCRIPT_DIR}

# Create Ranger repositories
HOST=$(hostname)
for service in hdfs hbase hive knox; do
    sed -e "s/_TYPE_/${service}/g" \
        -e "s/_CLUSTER_NAME_/${CLUSTER_NAME}/" \
        -e "s/_RANGER_USER_/${RANGER_USER}/" \
        -e "s/_RANGER_PASSWORD_/${RANGER_PASSWORD}/" \
        -e "s/_HOST_/${HOST}/" \
        resources/ranger-${service}-repo-template.json > ranger-repo-${service}.json
    curl -u $RANGER_USER:$RANGER_PASSWORD \
        -H 'Content-Type: application/json' \
        -X POST \
        -d @ranger-repo-${service}.json \
        $RANGER_API/repository
done

# Restart services

# Stop
for service in HBASE HIVE KNOX HDFS; do
    curl -u $AMBARI_USER:$AMBARI_PASSWORD -s \
        -H 'X-Requested-By: ambari' -X PUT \
        -d "{\"RequestInfo\": {\"context\" :\"Stop ${service} via REST\"}, \"Body\": {\"ServiceInfo\": {\"state\": \"INSTALLED\"}}}" \
        $AMBARI_API/services/${service}
done

# Start
for service in HDFS HBASE KNOX HIVE; do
    curl -u $AMBARI_USER:$AMBARI_PASSWORD -i \
        -H 'X-Requested-By: ambari' -X PUT \
        -d "{\"RequestInfo\": {\"context\" :\"Start ${service} via REST\"}, \"Body\": {\"ServiceInfo\": {\"state\": \"STARTED\"}}}" \
        $AMBARI_API/services/${service} #| python -c 'import sys, json; print json.load(sys.stdin)["href"]')
done

# Wait for completion
COMPLETED=0
while [ "$COMPLETED" -eq 0 ]; do
    status=$(curl -s -u $AMBARI_USER:$AMBARI_PASSWORD -H 'X-Requested-By: ambari' -X GET ${href}?fields=Requests | python -c 'import json, sys; print json.load(sys.stdin)["Requests"]["request_status"]')
    if [ "$status" = "COMPLETED" ]; then
        echo "Requests completed"
        COMPLETED=1
    else
        echo "Waiting for requests to be ready..."
        sleep 60
    fi
done

# create user and hdfs, hive, ... resources
USERS="sandbox alice bob"
USER_PASSWD="had00p"
for user in $USERS; do
    adduser -m -p $(openssl passwd $USER_PASSWD) -G hadoop $user
    su hdfs -c "hdfs dfs -mkdir /user/$user"
    su hdfs -c "hdfs dfs -chown $user:$user /user/$user"
    su $user -c "hive -e 'create database $user'"
done;

# TODO - Add default ranger policies
# TODO - Upload client libraries to HDFS




