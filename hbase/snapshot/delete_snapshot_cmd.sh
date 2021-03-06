#! /bin/sh
##
## Create commands to delete HBase snapshots
## 
## ./delete_snapshot_cmd.sh snapshot1 | hbase shell

usage() {
  echo "Usage:"
  echo "\t $0 SNAPSHOT_NAME"
}
if [ -z "$1" ]; then
  echo "snapshot name missing"
  usage
  exit 1
fi
SNAPSHOT_NAME="$1"

TABLES="table1
table2
namespace1:table
"

for table in $TABLES; do
    echo "delete_snapshot 'snapshot-${table/:/-}-${SNAPSHOT_NAME}'"    
done;
