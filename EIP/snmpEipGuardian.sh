#!/bin/bash

if [ "$#" -ne 2 ]; then
        echo "You must provide host IP address and community string for SNMPv2"
        echo "Usage: $0 [host.ip.address] [community]"
        exit 0
fi

HOST=$1
COMMUNITY=$2

readonly NOERROR='.1.3.6.1.4.1.2440.1.11.2.4.101.0'
readonly FORMERR='.1.3.6.1.4.1.2440.1.11.2.4.102.0'
readonly SERVFAIL='.1.3.6.1.4.1.2440.1.11.2.4.103.0'
readonly NXDOMAIN='.1.3.6.1.4.1.2440.1.11.2.4.104.0'
readonly NOTIMP='.1.3.6.1.4.1.2440.1.11.2.4.105.0'
readonly REFUSED='.1.3.6.1.4.1.2440.1.11.2.4.106.0'
readonly YXDOMAIN='.1.3.6.1.4.1.2440.1.11.2.4.107.0'
readonly YXRRSET='.1.3.6.1.4.1.2440.1.11.2.4.108.0'
readonly NXRRSET='.1.3.6.1.4.1.2440.1.11.2.4.109.0'
readonly NOTAUTH='.1.3.6.1.4.1.2440.1.11.2.4.120.0'
readonly NOTZONE='.1.3.6.1.4.1.2440.1.11.2.4.121.0'

echo "Getting BIND Answers..."
NOERROR_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NOERROR | awk '{ print$(4)};')
FORMERR_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $FORMERR | awk '{ print$(4)};')
SERVFAIL_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $SERVFAIL | awk '{ print$(4)};')
NXDOMAIN_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NXDOMAIN | awk '{ print$(4)};')
NOTIMP_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NOTIMP | awk '{ print$(4)};')
REFUSED_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $REFUSED | awk '{ print$(4)};')
YXDOMAIN_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $YXDOMAIN| awk '{ print$(4)};')
NXRRSET_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NXRRSET | awk '{ print$(4)};')
NOTAUTH_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NOTAUTH | awk '{ print$(4)};')
NOTZONE_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NOTZONE | awk '{ print$(4)};')

echo "NOERROR  = $NOERROR_VAL"
echo "FORMERR  = $FORMERR_VAL"
echo "SERVFAIL = $SERVFAIL_VAL"
echo "NXDOMAIN = $NXDOMAIN_VAL"
echo "NOTIMP   = $NOTIMP_VAL"
echo "REFUSED  = $REFUSED_VAL"
echo "YXDOMAIN = $YXDOMAIN_VAL"
echo "NXRRSET  = $NXRRSET_VAL"
echo "NOTAUTH  = $NOTAUTH_VAL"
echo "NOTZONE  = $NOTZONE_VAL"

echo  -e "\nFinished."
