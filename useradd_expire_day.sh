#!/bin/bash

# Source: http://mastersofthelinuxuniverse.blogspot.sg/2009/04/add-temporary-user-account.html
# Add Temporary User Account

function genPassword {
    printf "AutoPassword: "
    < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c8;echo;
    #genPass=`openssl rand -base64 8`
}

function printUse {
    printf  "Usage: useradd_expire.sh DAYS LOGIN\n\n"
    printf  "  DAYS               The number of days before account expires.\n"
    exit 1
}

if [[ $# -eq 2 && $1 -gt 0 ]]
    then
        expdate=`date -d "$1 days" +"%Y-%m-%d"`
        longdate=`date -d "$1 days" +"%a, %d %b %Y"`
        #echo "sudo useradd -g sftpusers -d /home/jails/ -s /sbin/nologin -e $expdate -c" '"Test Account"' $2

        sudo useradd -g sftpusers -d /home/jails/ -s /sbin/nologin -e $expdate -c "Temp Account" $2
        printf "Username: %s\n" $2
        genPassword

        sudo passwd $2

        echo "User created. Account Expires on $longdate"
    else
        printUse
fi
