##
## Recreate an HBase table given the current split points
##
include Java
import org.apache.hadoop.hbase.HBaseConfiguration
import org.apache.hadoop.hbase.client.HTable
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.hbase.client.HBaseAdmin

config = HBaseConfiguration.create()
cmd = HBaseAdmin.new(config)

table_name = ARGV[0]

# Get current region splits
table = HTable.new(cmd.getConfiguration(), table_name)
start_keys = table.getStartKeys()[1..-1]
table.close()

# recreate the table
table_descriptor = cmd.getTableDescriptor(Bytes.toBytes(table_name))
cmd.disableTable(table_name)
cmd.deleteTable(table_name)
cmd.createTable(table_descriptor, start_keys)
