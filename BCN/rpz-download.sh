#!/bin/bash
echo "Downloading latest database from Kominfo..."
#curl -kL https://trustpositif.kominfo.go.id/downloaddb.php -o domains

echo "Deleting leftover files..."
rm -rfv rpz.kominfo.db

soasn=`date +%s`
soarc="\$TTL    86400\n\
@       IN      SOA     ns1.kominfo.go.id. rpzmaster.kominfo.go.id. (\n\
\t\t$soasn\t; Serial\n\
\t\t10800\t\t; Refresh\n\
\t\t10800\t\t; Retry\n\
\t\t604800\t\t; Expire\n\
\t\t3600 )\t\t; Negative Cache TTL\n\
;\n\
@       IN      NS      ns1.kominfo.go.id.\n\
;"
echo -e $soarc >> rpz.kominfo.db
sed -E ':a;N;$!ba;s/\r{0,1}\n/\            CNAME .\n/g' domains >> rpz.kominfo.db
echo .
echo "BIND DB Ready: rpz.kominfo.db"
