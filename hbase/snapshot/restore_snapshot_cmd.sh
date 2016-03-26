#! /bin/sh
##
## Create commands to restore HBase snapshots 
## 
## ./restore_snapshot_cmd.sh snapshot1 | hbase shell

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
    echo "disable '${table}'"
    echo "restore_snapshot 'snapshot-${table/:/-}-${SNAPSHOT_NAME}'"
    echo "enable '${table}'"
done;
