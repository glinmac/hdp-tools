#!/bin/sh
##
## examples of API calls
##

AMBARI_USER=admin
AMBARI_PASSWORD=
CLUSTER_NAME=sandbox
AMBARI_API=http://127.0.0.1:8080/api/v1/clusters/$CLUSTER_NAME
BLUEPRINT_API=http://127.0.0.1:8080/api/v1/blueprints

hostname="hostname.example.com"
service="aservice"

# Stop service
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' \
  -X PUT \
  -d "{\"RequestInfo\":{\"context\":\"Stop Service $service\"},\"Body\":{\"ServiceInfo\":{\"state\":\"INSTALLED\"}}}" \
  $AMBARI_API/services/$service

# Delete service
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' \
  -X DELETE $AMBARI_API/services/$service

# Install component on a node
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i  -H 'X-Requested-By: ambari' \
  -X POST $AMBARI_API/hosts/$hostname/host_components/$service

curl -u $AMBARI_USER:$AMBARI_PASSWORD -i  -H 'X-Requested-By: ambari' \
  -X PUT -d '{"HostRoles": {"state": "INSTALLED"}}' \
  $AMBARI_API/hosts/HOSTNAME/host_components/$service

# Remove component on a node
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' \
  -X PUT -d '{"HostRoles": {"state": "INSTALLED"}}' \
  $AMBARI_API/hosts/$hostname/host_components/$service

curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari'\
  -X DELETE $AMBARI_API/hosts/$hostname/host_components/$service


# Delete cluster
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' -X DELETE $AMBARI_API

## Blueprints (https://cwiki.apache.org/confluence/display/AMBARI/Blueprints)

# Get blueprint
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' -X GET $AMBARI_API?format=blueprint

# Register blueprint
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' -X POST -d @topology.json $BLUEPRINT_API/topology-name

# Create cluster
curl -u $AMBARI_USER:$AMBARI_PASSWORD -i -H 'X-Requested-By: ambari' -X POST -d @cluster-creation.json  $AMBARI_API
