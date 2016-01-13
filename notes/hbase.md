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
       
