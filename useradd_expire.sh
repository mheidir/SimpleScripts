#!/bin/bash

# Source: http://mastersofthelinuxuniverse.blogspot.sg/2009/04/add-temporary-user-account.html
# Add Temporary User Account

function genPassword {
    printf "AutoPassword: "
    < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c8;echo;
    #genPass=`openssl rand -base64 8`
}

function checkDateFormat {
    if [[ $1 =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]
        then
            #echo "Valid Format: $1"
            return 1 #Valid format
        else
            #echo "Invalid Format: $1"
            return 0 #Invalid format
    fi
}

function printUse {
    printf "Usage: useradd_expire.sh EXPIRE_DATE LOGIN\n\n"
    printf "  EXPIRE_DATE        The date on which the user account will be disabled.\n"
    printf "                     The date is specified in the format YYYY-MM-DD.\n\n"
    exit 1
}

#if [[ $# -eq 2 || checkDateFormat -eq 1 ]]
    then
        #echo "sudo useradd -g sftpusers -d /home/jails/ -s /sbin/nologin -e $1 -c" '"Test Account"' $2
        sudo useradd -g sftpusers -d /home/jails/ -s /sbin/nologin -e $1 -c "Temp Account" $2
        printf "Username: %s\n" $2
        genPassword

        sudo passwd $2

        echo "User created. Account Expires on $1"
    else
        printUse
fi
