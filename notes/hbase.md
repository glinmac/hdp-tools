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

Service | Parameter |
--- | --- |
HBase Master           | hbase.master.ipc.address
HBase Master UI        | hbase.master.info.bindAddress
HBase Region Server UI | hbase.regionserver.info.bindAddress
HBase Region Server    | hbase.regionserver.ipc.address
       
## Export

    hbase org.apache.hadoop.hbase.mapreduce.Export <tablename> <outputdir> [<versions> [<starttime> [<endtime>]]]
    
If YARN/Mapreduce is not available and/or you want to test using only local resources:

* Hadoop 1

        hbase org.apache.hadoop.hbase.mapreduce.Export -Dmapred.job.tracker=local ....
        
* Hadoop2 (YARN)

        hbase org.apache.hadoop.hbase.mapreduce.Export -Dmapreduce.framework.name=local ...
        
