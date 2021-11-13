#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "You must provide host IP address and community string for SNMPv2"
	echo "Usage: $0 [host.ip.address] [community]"
	exit 0
fi

HOST=$1
COMMUNITY=$2

readonly SUCCESS='.1.3.6.1.4.1.2440.1.4.2.3.1.3.7.115.117.99.99.101.115.115'
readonly FAILURE='.1.3.6.1.4.1.2440.1.4.2.3.1.3.7.102.97.105.108.117.114.101'
readonly FORMERR='.1.3.6.1.4.1.2440.1.4.2.3.1.3.7.102.111.114.109.101.114.114'
readonly SERVFAIL='.1.3.6.1.4.1.2440.1.4.2.3.1.3.8.115.101.114.118.102.97.105.108'
readonly NXDOMAIN='.1.3.6.1.4.1.2440.1.4.2.3.1.3.8.110.120.100.111.109.97.105.110'
readonly NXRRSET='.1.3.6.1.4.1.2440.1.4.2.3.1.3.7.110.120.114.114.115.101.116'

echo "Getting BIND Answers..."
SUCCESS_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $SUCCESS | awk '{ print$(4)};')
FAILURE_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $FAILURE | awk '{ print$(4)};')
FORMERR_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $FORMERR | awk '{ print$(4)};')
SERVFAIL_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $SERVFAIL | awk '{ print$(4)};')
NXDOMAIN_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NXDOMAIN | awk '{ print$(4)};')
NXRRSET_VAL=$(snmpget -v2c -c $COMMUNITY $HOST $NXRRSET | awk '{ print$(4)};')

echo "SUCCESS  = $SUCCESS_VAL" 
echo "FAILURE  = $FAILURE_VAL" 
echo "FORMERR  = $FORMERR_VAL" 
echo "SERVFAIL = $SERVFAIL_VAL" 
echo "NXDOMAIN = $NXDOMAIN_VAL" 
echo "NXRRSET  = $NXRRSET_VAL" 

echo  -e "\nFinished."
exit 0