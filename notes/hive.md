# Hive

## Doc

* http://hive.apache.org

## Misc

* Beeline connection string:
  * Standard

            !connect jdbc:hive2://<HOST>:10000/<DATABASE>
  * Kerberos

            !connect jdbc:hive2://<HOST>:10000/<DATABASE>;principal=hive/<HIVESERVER2_HOST>@<REALM>

  * HTTP

            !connect jdbc:hive2://<HOST>:10000/<DATABASE>;hive.server2.transport.mode=http;hive.server2.thrift.http.path=<http_endpoint>
  * SSL

            !connect jdbc:hive2://<HOST>:10000/<DATABASE>;ssl=true;sslTrustStore=<path>;trustStorePassword=<password>
