# HBase

## Doc

* http://hbase.apache.org

* [HBase Book](http://hbase.apache.org/book.html)
* [Transparent encryption](http://hbase.apache.org/book.html#hbase.encryption.server)
* [Cell level ACLs](http://hbase.apache.org/book.html#hbase.accesscontrol.configuration)

## Tools

* HFile inspection tool

        hbase org.apache.hadoop.hbase.io.hfile.HFile ...

* Address on which the servers listen:

Service | Property
------- | ---------
HBase Master IPC | `hbase.master.ipc.address`
HBase Master IPC port | `hbase.master.port`
HBase Master UI |	`hbase.master.info.bindAddress`
HBase Master UI port | `hbase.master.info.port`
HBase Master Hostname |	`hbase.master.hostname`
HBase Region Server IPC | `hbase.regionserver.ipc.address`
HBase Region Server IPC port| `hbase.regionserver.port`
HBase Region Server UI | `hbase.regionserver.info.bindAddress`
HBase Region Server UI port | `hbase.regionserver.info.port`
HBase Region Server Hostname ([HBASE-12954]) | `hbase.regionserver.hostname`

[HBASE-12954]: https://issues.apache.org/jira/browse/HBASE-12954
       
## Export

    hbase org.apache.hadoop.hbase.mapreduce.Export <tablename> <outputdir> [<versions> [<starttime> [<endtime>]]]
    
If YARN/Mapreduce is not available and/or you want to test using only local resources:

* Hadoop 1

        hbase org.apache.hadoop.hbase.mapreduce.Export -Dmapred.job.tracker=local ....
        
* Hadoop2 (YARN)

        hbase org.apache.hadoop.hbase.mapreduce.Export -Dmapreduce.framework.name=local ...
        
## Snapshot

* Create a snapshot of all tables (named $TABLE-ru-$date, eg `myTable-ru-20160314`, only one snapshot for a given day)

        snapshot_all
        snapshot_all 'table_.*'
    
* Create a snapshot of one table:

        snapshot 'myTable', 'mySnaphot'
        
* List snapshots

        list_snapshots
        list_snapshots 'snapshotname.*'
        list_snapshots '.*20160313.*'

* Restore a snapshot of a table:

        disable 'myTable'
        restore_snapshot 'myTable', 'mySnapshot'
        enable 'myTable'

* Restore all snapshots for a given date

        snapshot_restore '20160316'
       
* Delete snapshot

        delete_snapshot 'mySnapshot'

* Delete all snapshot

        delete_all

* Clone from snapshot

        clone_snapshot 'mySnapshot', 'myNewTable'
   
 
    
    
    
