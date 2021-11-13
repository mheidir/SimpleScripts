#!/bin/sh

####################################################
# System Variables
# Please modify as necessary based on environment

#########################
# RSYNC Server Settings #
RSYNCSRV="10.0.10.120"
RSYNCPORT=873

#############################################
# SOLIDserver - Central Management Settings #
XIPMSERVERURL='https://172.16.16.21/rest'
XIPMUSER='eW91YXJlbG9va2luZw=='
XIPMPASS='cGFzc3dvcmQ='

DNSNAME='smart.kisa.or.kr'

##################################
# SOLIDserver Directory and File #
HOMEDIR="/data1/users/admin"
KFILE="$HOMEDIR/sinkhole_forward.conf"

####################################################
# Script Start

# If file exists, rename file
if [ -f "$KFILE" ]
then
        echo "[NOTICE] File exists, renaming current file"
        mv "$KFILE" "$KFILE.tmp"
fi

# Check if file does not exist, download
if [ ! -f "$KFILE" ]
then
        echo "[NOTICE] File does not exist, downloading from server for latest version"
        rsync -rtuvz --progress --port="$RSYNCPORT" "$RSYNCSRV"::cnc_bind_new $HOMEDIR
fi

if [ ! $? -eq 0 ]
then
        echo "[ERROR] rsync failed to connect to server. Aborting script."
        exit 1
fi

# Compare file hash to identify if there is any change
echo "Comparing files..."
cmp -s "$KFILE" "$KFILE.tmp"
if [ $? -eq 0 ]
then
        echo "[NOTICE] Files are the same, no update required"
        rm -rfv "$KFILE.tmp"
        echo "Script terminating"
        exit 0
fi

echo "[NOTICE] Contents are different."

echo "[NOTICE] Total Lines: $(wc -l $KFILE | awk '{ print $1; }')"
COUNTER=0

echo "[NOTICE] Reading file and updating into SOLIDserver"

while IFS= read -r line
do
        ZONE=$(echo "$line" | cut -d'"' -f2)
        FORWARDER=$(echo "$line" | cut -d'{' -f3 | cut -d';' -f1)

        # DEBUG
        #echo "$XIPMSERVERURL/dns_zone_add?dnszone_name=$ZONE&dnszone_type=forward&dnszone_forwarders=$FORWARDER;&dnsview_id=0&dnszone_forward=only&dns_name=$DNSNAME"
        #echo "x-ipm-username: $XIPMUSER"
        #echo "x-ipm-password: $XIPMPASS"

        curl -k --silent --output /dev/null "$XIPMSERVERURL/dns_zone_add?dnszone_name=$ZONE&dnszone_type=forward&dnszone_forwarders=$FORWARDER;&dnsview_id=0&dnszone_forward=only&dns_name=$DNSNAME" -X POST -H "x-ipm-username: $XIPMUSER" -H "x-ipm-password: $XIPMPASS" > /dev/null

        if [ ! $? -eq 0 ]
        then
                echo "[ERROR] curl failed to connect to server. Aborting script."
                exit 1
        fi

        COUNTER=$(($COUNTER+1))
        echo -n "$COUNTER "

        # DEBUG
        # if [ $COUNTER -eq 10 ]
        # then
        #       exit 0
        #fi
done < "$KFILE"

# Cleaning up temporary file
rm -rfv "$KFILE.tmp"

echo "[NOTICE] Zones update complete."
exit 0
