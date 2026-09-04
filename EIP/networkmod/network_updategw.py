#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2026, Muhammad Heidir
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import csv
import socket
import base64
import json
import time
import urllib3
import requests
import ipaddress

# Suppress insecure request warnings (mimics the `curl -k` flag)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = "sds.conf"

class Solidserver:
    def __init__(self, sds_host, sds_username, sds_password):
        self.sds_host = sds_host

        # Encode credentials in base64
        self.sds_username = base64.b64encode(sds_username.encode('utf-8')).decode('utf-8')
        self.sds_password = base64.b64encode(sds_password.encode('utf-8')).decode('utf-8')


def read_config(filepath):
    """
    Reads the config file, splitting keys and values,
    and stripping out standard and smart quotes.
    """
    config = {}
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                # Ignore empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    
                    # Clean the value (strip whitespace and all quote types)
                    clean_value = value.strip()
                    for char in ['"', "'", '“', '”']:
                        clean_value = clean_value.replace(char, '')
                        
                    config[key.strip()] = clean_value
    except FileNotFoundError:
        print(f"[ERROR] Configuration file '{filepath}' not found.")
        sys.exit(1)
        
    return config

def getIpfromHex(hex_value):
    """
    Reads the hexadecimal value and convert to IPv4 address
    
    :param hex_value: Hexadecimal value of IPv4 address to be converted
    """
    return ipaddress.IPv4Address(int(hex_value, 16))

def getHexfromIp(ipv4_value):
    """
    Reads the IPv4 address and hexadecimal value
    
    :param ipv4_value: IPv4 address to be converted to Hexadecimal
    """
    return ipaddress.IPv4Address(ipv4_value).packed.hex()

def getCsvDataAsDict(filename):
    """
    Read CSV file and return data as JSON

    :param filename: path to the file and its filename
    """
    try:
        with open(filename, mode='r', encoding='utf-8-sig') as file:
            # Read the CSV into a list of dictionaries
            csv_reader = csv.DictReader(file, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_list = list(csv_reader)

            for row in csv_list:
                start_ip = row['Start']
                print(f'[INFO] Identified Network: {start_ip}')

            # list() consumes the reader and creates a list containing a dict for each row
            return csv_list
            
    except FileNotFoundError:
        print(f"[ERROR] File '{filename}' not found.")
        sys.exit(1)
    except KeyError:
        print(f"[ERROR] The file '{filename}' does not contain a 'Start' column.")
        sys.exit(1)

def updateDhcpGw(solidserver, csv_row):
    """
    Update gateway from DHCP Scope
    
    :param solidserver: Solidserver class containing the host, username and password
    :param csv_row: CSV row data containing the information required (Start, Space)
    """
    print(f'[INFO] Updating new gateway address: {csv_row['option routers']}')
    api_url = f"{solidserver.sds_host.rstrip('/')}/rest/dhcp_option_add"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    # Payload containing the mandatory Gateway update parameters
    payload = {
        "dhcpoption_type": "scope",
        "dhcpscope_id": csv_row['dhcpscope_id'],
        "dhcpoption_name": "option routers",
        "dhcpoption_value": csv_row['option routers'].replace(';',"")
    }

    try:
        # Use the json= argument instead of data= to let requests handle serialization and headers automatically
        response = requests.post(api_url, headers=headers, json=payload, verify=False)
        
        response.raise_for_status()

        # To verify what URL requests actually generated, you can print:
        print("[INFO] Requested URL:", response.url)
        
        # Check the API response
        if response.status_code > 299:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            return False
        else:
            time.sleep(2)
            print(f"[INFO] Successfully updated Gateway: {csv_row['option routers']}")
            return True
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API call failed: {e}")

def updateSubnetGw(solidserver, csv_row):
    """
    Update gateway from IP Subnet
    
    :param solidserver: Solidserver class containing the host, username and password
    :param csv_row: CSV row data containing the information required (Start, Space)
    """
    print(f'[INFO] Updating new gateway address: {csv_row['option routers']}')
    api_url = f"{solidserver.sds_host.rstrip('/')}/rest/ip_subnet_add"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    # Payload containing the mandatory Gateway update parameters
    payload = {
        "subnet_id": csv_row['subnet_id'],
        "network_class_parameters": f'gateway={csv_row['option routers'].replace(';',"")}'
    }

    try:
        # Use the json= argument instead of data= to let requests handle serialization and headers automatically
        response = requests.put(api_url, headers=headers, json=payload, verify=False)
        
        response.raise_for_status()

        # To verify what URL requests actually generated, you can print:
        print("[INFO] Requested URL:", response.url)
        
        # Check the API response
        if response.status_code > 299:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            return False
        else:
            time.sleep(2)
            print(f"[INFO] Successfully updated Gateway: {csv_row['option routers']}")
            return True
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API call failed: {e}")

def getDhcpScopeData(solidserver, csv_row):
    """
    Retrieve DHCP data based on the network and space information
    
    :param solidserver: Solidserver class containing the host, username and password
    :param csv_row: CSV row data containing the information required (Start, Space)
    """
    print(f'[INFO] Retrieving DHCP data for network: {csv_row['Start']}')

    api_url = f"{solidserver.sds_host.rstrip('/')}/rest/dhcp_scope_list"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Accept": "application/json"
    }

    # 1. Build the exact clause you want
    # The variables are injected inside the single quotes
    where_clause = f"dhcpscope_net_addr='{csv_row['Start']}' AND dhcpscope_site_name='{csv_row['Space']}'"

    # Pass it to the params dictionary
    params = {
        "WHERE": where_clause
    }

    try:
        # Execute the API call (verify=False ignores self-signed certs like curl -k)
        response = requests.get(api_url, headers=headers, params=params, verify=False)
        
        # To verify what URL requests actually generated, you can print:
        print("[INFO] Requested URL:", response.url)

        if response.status_code != 200:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            sys.exit(1)
            
        print("[INFO] Success: API returned 200 OK.")
        
        return response.json()
        
        # Example of how you can now interact with the JSON response
        # print(json.dumps(json_data, indent=4))
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        return
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from the API response.")
        print(f"[ERROR] Raw Output: {response.text}")
        return

def getIpBlockSubnetList(solidserver, csv_row):
    """
    Retrieve IP Block Subnet List
    
    :param solidserver: Solidserver class containing the host, username and password
    :param csv_row: CSV row data containing the information required (dhcpscope_id)
    """
    print(f'[INFO] Retrieving IP Block Subnet: {csv_row['Start']}')

    api_url = f"{solidserver.sds_host.rstrip('/')}/rest/ip_block_subnet_list"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Accept": "application/json"
    }

     # 1. Build the exact clause you want
    # The variables are injected inside the single quotes
    where_clause = f"site_name='{csv_row['Space']}' AND start_hostaddr='{csv_row['Start']}'"

    # Pass it to the params dictionary
    params = {
        "WHERE": where_clause
    }

    try:
        # Execute the API call (verify=False ignores self-signed certs like curl -k)
        response = requests.get(api_url, headers=headers, params=params, verify=False)
        
        # To verify what URL requests actually generated, you can print:
        print("[INFO] Requested URL:", response.url)

        if response.status_code != 200:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            return []
            
        print("[INFO] Success: API returned 200 OK.")
        
        return response.json()
        
        # Example of how you can now interact with the JSON response
        # print(json.dumps(json_data, indent=4))
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        return []
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from the API response.")
        print(f"[ERROR] Raw Output: {response.text}")
        return []
    
def getIpBlockSubnetInfo(solidserver, csv_row):
    """
    Retrieve IP Block Subnet List
    
    :param solidserver: Solidserver class containing the host, username and password
    :param csv_row: CSV row data containing the information required (dhcpscope_id)
    """
    print(f'[INFO] Retrieving IP Block Subnet: {csv_row['Start']}')

    api_url = f"{solidserver.sds_host.rstrip('/')}/rest/ip_block_subnet_info"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Accept": "application/json"
    }

    params = {
        "subnet_id": csv_row['subnet_id'],
        "TAGS": 'network.gateway'
    }

    try:
        # Execute the API call (verify=False ignores self-signed certs like curl -k)
        response = requests.get(api_url, headers=headers, params=params, verify=False)
        
        # To verify what URL requests actually generated, you can print:
        print("[INFO] Requested URL:", response.url)

        if response.status_code != 200:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            return []
            
        print("[INFO] Success: API returned 200 OK.")
        
        return response.json()
        
        # Example of how you can now interact with the JSON response
        # print(json.dumps(json_data, indent=4))
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        return []
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from the API response.")
        print(f"[ERROR] Raw Output: {response.text}")
        return []

def getDhcpScopeOptionsData(solidserver, csv_row):
    """
    Retrieve DHCP Scope options
    
    :param solidserver: Solidserver class containing the host, username and password
    :param csv_row: CSV row data containing the information required (dhcpscope_id)
    """
    print(f'[INFO] Retrieving DHCP Scope options for network: {csv_row['Start']}')

    api_url = f"{solidserver.sds_host.rstrip('/')}/rest/dhcp_scope_options_list"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Accept": "application/json"
    }

    # Pass it to the params dictionary
    params = {
        "dhcpscope_id": csv_row['dhcpscope_id']
    }

    try:
        # Execute the API call (verify=False ignores self-signed certs like curl -k)
        response = requests.get(api_url, headers=headers, params=params, verify=False)
        
        # To verify what URL requests actually generated, you can print:
        print("[INFO] Requested URL:", response.url)

        if response.status_code != 200:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            sys.exit(1)
            
        print("[INFO] Success: API returned 200 OK.")
        
        return response.json()
        
        # Example of how you can now interact with the JSON response
        # print(json.dumps(json_data, indent=4))
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        return []
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from the API response.")
        print(f"[ERROR] Raw Output: {response.text}")
        return []

def checkApiConnectivity(solidserver):
    """
    Checks connectivity to the SOLIDserver by making an API call
    
    :param solidserver: SOLIDserver class containing the connection and credentials
    """
    api_url = f"{solidserver.sds_host.rstrip('/')}/api/v2.0/ipam/space/list"
    
    headers = {
        "X-IPM-Username": solidserver.sds_username,
        "X-IPM-Password": solidserver.sds_password,
        "Accept": "application/json"
    }

    try:
        # Execute the API call (verify=False ignores self-signed certs like curl -k)
        response = requests.get(api_url, headers=headers, verify=False)
        
        if response.status_code != 200:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            sys.exit(1)
            
        print("[INFO] Success: API returned 200 OK.")
        
        # ==========================================================================
        # 3. JSON Handling
        # ==========================================================================
        # Because we are using Python, extracting JSON is native and simple:
        json_data = response.json()
        
        # Example of how you can now interact with the JSON response
        # print(json.dumps(json_data, indent=4))
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from the API response.")
        print(f"[ERROR] Raw Output: {response.text}")
        sys.exit(1)

def outputCsvFile(dict_input, file_name):
    all_columns = []
    for row in dict_input:
        for key in row.keys():
            if key not in all_columns:
                all_columns.append(key)

    # 2. Write the data to a new CSV
    with open(file_name, mode='w', encoding='utf-8', newline='') as file:
        # Initialize the DictWriter with our gathered column headers
        writer = csv.DictWriter(file, fieldnames=all_columns, quoting=csv.QUOTE_ALL)
        
        # Write the header row
        writer.writeheader()
        
        # Write all the dictionary rows (missing keys will just be left blank)
        writer.writerows(dict_input)


def main():# The variables are injected inside the single quotes
    # ==============================================================================
    # 1. Checks for argument and a valid CSV file
    # ==============================================================================
    # Check if a filename argument was provided
    # sys.argv[0] is the script name, sys.argv[1] is the first argument
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <path_to_csv_file>")
        sys.exit(1) # Exit the script with an error code

    # Get the filename from the command line arguments
    filename = sys.argv[1]

    # Retrieve CSV data as Dict
    csvdata = getCsvDataAsDict(filename)

    # ==============================================================================
    # 2. Obtain SOLIDserver Configuration
    # ==============================================================================
    config = read_config(CONFIG_FILE)

    sds_host = config.get("SDSHOST")
    sds_username = config.get("SDSUSERNAME")
    sds_password = config.get("SDSPASSWORD")

    if not all([sds_host, sds_username, sds_password]):
        print("[ERROR] Missing required configuration parameters in sds.conf.")
        sys.exit(1)

    # Create an instance of the credential and host
    sds = Solidserver(sds_host, sds_username, sds_password)

    # ==============================================================================
    # 3. Check API Connectivity
    # ==============================================================================
    print("[INFO] Testing API connection to SOLIDserver...")
    checkApiConnectivity(sds)

    for row_data in csvdata:
        currentGw = ""
        ipBlockSubnetData = getIpBlockSubnetList(sds, row_data)
        for opt_name in ipBlockSubnetData:
            row_data['subnet_id'] = opt_name['subnet_id']
        
        
        ipBlockSubnetInfo = getIpBlockSubnetInfo(sds, row_data)
        row_data['gateway'] = ipBlockSubnetInfo[0]['tag_network_gateway']
        currentGw = ipBlockSubnetInfo[0]['tag_network_gateway']

        dhcpScopeData = getDhcpScopeData(sds, row_data)
        row_data['dhcpscope_id'] = dhcpScopeData[0]['dhcpscope_id']

        #dhcpScopeOptionsData = getDhcpScopeOptionsData(sds, row_data)
        #for opt_name in dhcpScopeOptionsData:
        #    if opt_name['dhcpoption_name'] == 'option routers':
        #        print(f'[INFO] Configured Gateway: {opt_name['dhcpoption_value']}')
        #        currentGw = opt_name['dhcpoption_value']
        #    if opt_name['dhcpscope_id'] in opt_name:
        #        row_data['dhcpscope_id'] = opt_name['dhcpscope_id']
        
        if currentGw != row_data['option routers'].replace(';',''):
            print(f'[WARN] Gateway does not match: {row_data['option routers']}')
            #gwstatus = updateGw(sds, row_data)
            gwstatus = updateSubnetGw(sds, row_data)

            time.sleep(2)
            print(f'[INFO] Validating gateway change...')
            dhcpScopeOptionsData = getDhcpScopeOptionsData(sds, row_data)
            for opt_name in dhcpScopeOptionsData:
                if opt_name['dhcpoption_name'] == 'option routers':
                    print(f'[INFO] Configured Gateway: {opt_name['dhcpoption_value']}')
                    if opt_name['dhcpoption_value'] == row_data['option routers']:
                        print(f'[INFO] Gateway updated successfully!')
                    else:
                        print(f'[ERROR] Gateway update failed. Please check settings.')
        else:
            print(f'[INFO] No change to gateway: {currentGw}')

    sys.exit(0)

    #print(csvdata)
    #outputCsvFile(csvdata, 'network_compiled.csv')


# ==============================================================================
# Start Execution
# ==============================================================================
if __name__ == "__main__":
    main()