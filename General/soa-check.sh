#!/bin/bash

# Copyright 2025 Muhammad Heidir
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: Muhammad Heidir
# Date: 2025-07-11
# Version: 1.0.1
# Description: Compare SOA between Primary and Secondary DNS from a list of zones
# Prerequisites: Zone list file must be in CSV format comprising of the following fields: zone, type, view

if [ $# -eq 0 ]; then
	echo "[ERROR] $0 input.file output.file primaryDNS.IP secondaryDNS.IP"
	exit 1
fi

# START EXECUTION

FILE_IN=$1
FILE_OUT=$2

PRIDNS=$3
SECDNS=$4

IFS=','
COUNT=0
TOTALCNT=0

printf "%-30s %6s\t\t %10s\t %10s\t Result\n" "Zone" "View" "P:$PRIDNS" "S:$SECDNS"

while read -r zone type view zonescope authority signed
do
	TOTALCNT=$((TOTALCNT+1))
	
	if [[ "$zone" == *.* && "$type" == *"Primary"* ]]; then
		#echo -e "[INFO] Zone: $zone\t Type: $type\t View: $view"
		
		PRI_RESULT=$(nslookup -type=SOA $zone $PRIDNS)
		if [[ "$PRI_RESULT" == *"serial"* ]]; then
			PRI_SN=$(echo $PRI_RESULT | grep serial | awk '{ print $3; }')
		else
			PRI_SN=$(echo $PRI_RESULT | grep $zone | awk '{ print $6; }')
		fi
		
		SEC_RESULT=$(nslookup -type=SOA $zone $SECDNS)
		if [[ "$SEC_RESULT" == *"serial"* ]]; then
			SEC_SN=$(echo $SEC_RESULT | grep serial | awk '{ print $3; }')
		else
			SEC_SN=$(echo $SEC_RESULT | grep $zone | awk '{ print $6; }')
		fi
		
		if [[ "$PRI_SN" -eq "$SEC_SN" && "$SEC_SN" != *"REFUSED"* && "$SEC_SN" != *"SERVFAIL"* ]]; then
			printf "%-30s\t %-10s\t %-10s\t\t %-10s\t\t OK\n" ${zone:0:30} $view $PRI_SN $SEC_SN 
			echo "$zone,$PRI_SN,$SEC_SN,OK" >> $FILE_OUT
		else
			printf "%-30s\t %-10s\t %-10s\t\t %-10s\t\t BAD\n" ${zone:0:30} $view $PRI_SN $SEC_SN 
			echo "$zone,$PRI_SN,$SEC_SN,BAD" >> $FILE_OUT
		fi		
		
    	COUNT=$((COUNT+1))
		
		#if [[ "$COUNT" -eq 2 ]]; then
		#	exit 0
		#fi
	else
		if [[ "$type" == *"Secondary"* ]]; then
			printf "%-30s\t %-10s\t %-10s\t\t %-10s\t\t BAD-Secondary Zone\n" ${zone:0:30} $view "SKIPPED" "SKIPPED" 
			echo "$zone,SKIPPED,SKIPPED,BAD - Secondary Zone" >> $FILE_OUT
		else
			printf "%-30s\t %-10s\t %-10s\t\t %-10s\t\t BAD-Check Config\n" ${zone:0:30} $view "SKIPPED" "SKIPPED" 
			echo "$zone,SKIPPED,SKIPPED,BAD - Check Configuration" >> $FILE_OUT
		fi
	fi
done < $FILE_IN

echo "[INFO] Total Primary Zones processed: $COUNT out of $TOTALCNT"
echo "[INFO] SOA Check Completed. Output File: $FILE_OUT"
exit 0 
