# KMS

## Doc


* https://hadoop.apache.org/docs/r2.6.0/hadoop-kms/index.html

## Misc

* Generate a keystore (hadoop 2.6.0)

        keytool -genkeypair -alias kms -keystore kms.keystore -storepass password

* Generate cert

        keytool -genkey -alias tomcat -keyalg RSA

