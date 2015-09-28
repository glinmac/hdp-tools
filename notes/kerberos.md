# Kerberos

## Doc

## Misc

* Veryfing groups resolved with HDFS:

        hdfs groups auser

* Verifying kerberos name

        hadoop org.apache.hadoop.security.HadoopKerberosName princ/server@REALM.COM

* Cross-realm authentication
    * This might help (see [HDFS-7546](https://issues.apache.org/jira/browse/HDFS-7546))

            dfs.namenode.kerberos.principal.pattern = *

* Managing keytabs
    * kt_util + read_kt, write_kt to merge keytabs


* Setting up kdc / centos6

        # Install packages
        yum install krb5-server krb5-libs krb5-auth-dialog krb5-workstation

        # edit /var/kerberos/krb5kdc/kdc.conf with appropriate changes (realm)
        # edit /etc/krb5.conf with appropriate changes (realm)

        # initialize db
        /usr/sbin/kdb5_util create –s

        # Add an admin user, eg:
        /usr/sbin/kadmin.local -q "addprinc root/admin"

        # modify kadm5.acl if necessary

        # start services
        service krb5kdc start
        service kadmin start

## Centrify

* adjoin

        adjoin -i -V -z <ZONE> -S <DOMAIN> -n <HOSTNAME>  

* adkeytab
* centrifydc
* adquery

## IPA

* Retrieveing keytabs

        ipa-getkeytab -s $IPA_SERVER -p $USER/$HOSTNAME@$REALM -k /path/to/a.keytab
        # optionally -P to init with a known password




