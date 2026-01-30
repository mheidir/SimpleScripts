# -*- coding: utf-8 -*-
#######################################################
# Copyright (c) 2020, Muhammad Heidir
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Title: Resource Record Generator
# Description: This Python script is used to generate Resource Record
#              in alphabetical order from a up to maximum of zzzzzz.
#              Required arguments to supply are the number of records
#              to be generated and the zone name:
#              python3 ./rrgenerator.sh 100 dummy.corp
#              python3 ./rrgenerator.sh <count> <zone>
#              Optional Argument: csv or query
#              Default: csv
#              csv output a comma delimited in the following format:
#              name,type,ipaddress = a.dummy.corp,A,1.0.0.0
#              query output a name and type for use with dnsperf or
#              blastbench:
#              name type = a.dummy.corp A
#              To store the output a text file, use cat '>'
#              python3 ./rrgenerator.py 100 dummy.corp > csv_output.txt
#
# Build: 0.1 - 6th January 2021
# Built with: python3.7
#
#!/usr/bin/python3

# Required libraries
import sys, argparse

arg_parser = argparse.ArgumentParser(description='Resource Record and IP Address Generator')
arg_parser.add_argument('Count', metavar='count', type=int, help='The number of items to generate')
arg_parser.add_argument('Zone', metavar='zone', type=str, help='Zone name to append to resource records')
arg_parser.add_argument('Format', metavar='format', type=str, nargs="?", default='csv', choices=['csv','query'], help='Format: csv or query, csv=name,type,ipddress, query=name type')
args = arg_parser.parse_args()

input_total = args.Count
input_zone = "." + args.Zone
input_format = args.Format

def generateRecords(total, zone, format):
	defaultValue = -65 # If null = -97
	finalString = [defaultValue, defaultValue, defaultValue, defaultValue, defaultValue, -1]

	ipAddress = [ 1, 0, 0, -1]

	for x in range(0, total):
		finalString[5] += 1
		ipAddress[3] += 1
		
		if ipAddress[3] == 256:
			ipAddress[2] += 1 
			ipAddress[3] = 0
			
		if ipAddress[2] == 256:
			ipAddress[1] += 1
			ipAddress[2] = 0
			ipAddress[3] = 0
			
		if ipAddress[1] == 256:
			ipAddress[0] += 1
			ipAddress[1] = 0
			ipAddress[2] = 0
			ipAddress[3] = 0
		
		# Skip reserved addresses
		# https://en.wikipedia.org/wiki/Reserved_IP_addresses
		if ipAddress[0] == 127:
			ipAddress[0] = 128
		
		if ipAddress[0] == 169:
			ipAddress[0] = 170
		
		if ipAddress[0] == 224:
			ipAddress[0] = 225
			
		if ipAddress[0] == 255:
			print("[STOP] Number of IPv4 address required exceeded available for use. Reduce count")
			sys.exit(0)
		
		if finalString[5] == 26:
			if finalString[4] == defaultValue:
				finalString[4] = 0
			else:
				finalString[4] += 1
			finalString[5] = 0
		
		if finalString[4] == 26:
			if finalString[3] == defaultValue:
				finalString[3] = 0
			else:
				finalString[3] += 1
			finalString[4] = 0
			finalString[5] = 0
			
		if finalString[3] == 26:
			if finalString[2] == defaultValue:
				finalString[2] = 0
			else:
				finalString[2] += 1
			finalString[3] = 0
			finalString[4] = 0
			finalString[5] = 0
			
		if finalString[2] == 26:
			if finalString[1] == defaultValue:
				finalString[1] = 0
			else:
				finalString[1] += 1
			finalString[2] = 0
			finalString[3] = 0
			finalString[4] = 0
			finalString[5] = 0
			
		if finalString[1] == 26:
			if finalString[0] == defaultValue:
				finalString[0] = 0
			else:
				finalString[0] += 1
			finalString[1] = 0
			finalString[2] = 0
			finalString[3] = 0
			finalString[4] = 0
			finalString[5] = 0
			
		if finalString[0] == 26:
			print("[STOP] Amount of required record count exceeded limit!")
			sys.exit(0)
		
		if format == "query":
			print (str.strip(chr(finalString[0] + 97)  + chr(finalString[1] + 97) + chr(finalString[2] + 97) + chr(finalString[2] + 97) + chr(finalString[3] + 97) + chr(finalString[4] + 97) + chr(finalString[5] + 97) + zone + " A" ))
		else:
			print (str.strip(chr(finalString[0] + 97)  + chr(finalString[1] + 97) + chr(finalString[2] + 97) + chr(finalString[2] + 97) + chr(finalString[3] + 97) + chr(finalString[4] + 97) + chr(finalString[5] + 97) + zone + ",A," + str(ipAddress[0]) + "." + str(ipAddress[1]) + "." + str(ipAddress[2]) + "." + str(ipAddress[3])))
		

generateRecords(input_total, input_zone, input_format)

sys.exit(0)