# Misc

## Keytool / cert

* Generate private key

        openssl genrsa -aes256 -out mykey.key 2048

* Create certificate request

        openssl req -new -key mykey.key -out mycsr.csr

* Add alternate names to CSR:

        Copy default openssl.cnf
        Add the following to openssl.cnf

        [req]
        req_extensions = v3_req

        [v3_req]
        subjectAltName = @alt_names

        [alt_names]
        DNS.1 = alias1
        DNS.2 = alias2

        gen cert request:

        openssl req -new -key mykey.key -out mycsr.csr -config openssl.cnf

* Check CSR

        openssl req -text -noout -in mycsr.csr
