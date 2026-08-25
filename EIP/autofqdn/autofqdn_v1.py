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
import socket
import base64
import json
import urllib3
import requests
import dns.resolver

# Suppress insecure request warnings (mimics the `curl -k` flag)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = "sds.conf"

def get_a_records(fqdn, nameserver=None):
    """
    Performs a DNS A-record lookup using dnspython.
    Resolves using the provided nameserver IP, or falls back to the system default.
    """
    try:
        if nameserver:
            # User provided an IP: Create a custom resolver targeting ONLY this IP
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = [nameserver]
            answers = resolver.resolve(fqdn, 'A')
        else:
            # User left it blank: Use the system's assigned DNS resolver
            answers = dns.resolver.resolve(fqdn, 'A')
            
        return [rdata.address for rdata in answers]
        
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return []
    except dns.exception.Timeout:
        print(f"[ERROR] DNS query timed out.")
        return []
    except Exception as e:
        print(f"[ERROR] DNS lookup failed: {e}")
        return []

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

def main():
    # ==============================================================================
    # 1. Handle FQDN Input & DNS Lookup
    # ==============================================================================
    if len(sys.argv) > 1:
        fqdn = sys.argv[1]
    else:
        fqdn = input("Enter the FQDN to lookup (e.g., www.example.com): ").strip()

    if not fqdn:
        print("[ERROR] FQDN cannot be empty.")
        sys.exit(1)

    # Ask for the specific DNS server IP
    dns_server = input("Enter the DNS server IP to query (leave blank to use system assigned DNS): ").strip()

    if dns_server:
        print(f"[INFO] Performing A record lookup for '{fqdn}' via DNS server {dns_server}...")
    else:
        print(f"[INFO] Performing A record lookup for '{fqdn}' via system assigned DNS...")

    # Pass the user input to the function (if blank, it passes None)
    ip_list = get_a_records(fqdn, nameserver=dns_server if dns_server else None)

    if not ip_list:
        print(f"[ERROR] No A records found for {fqdn}.")
        sys.exit(1)
    else:
        print(f"[INFO] Found {len(ip_list)} A record(s):")
        for ip in ip_list:
            print(f" - {ip}")
    # ==============================================================================
    # 2. Obtain SOLIDserver Configuration
    # ==============================================================================
    config = read_config(CONFIG_FILE)

    sds_host = config.get("SDSHOST")
    sds_username = config.get("SDSUSERNAME")
    sds_password = config.get("SDSPASSWORD")
    sds_gslbserver = config.get("GSLBSERVER")

    if not all([sds_host, sds_username, sds_password, sds_gslbserver]):
        print("[ERROR] Missing required configuration parameters in sds.conf.")
        sys.exit(1)

    # Encode credentials in base64
    b64_username = base64.b64encode(sds_username.encode('utf-8')).decode('utf-8')
    b64_password = base64.b64encode(sds_password.encode('utf-8')).decode('utf-8')

    # ==============================================================================
    # 3. Test API Connection to SOLIDserver
    # ==============================================================================
    print("[INFO] Testing API connection to SOLIDserver...")

    api_url = f"{sds_host.rstrip('/')}/api/v2.0/ipam/space/list"
    
    headers = {
        "X-IPM-Username": b64_username,
        "X-IPM-Password": b64_password,
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
        # 4. JSON Handling
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
        
        
    # ==============================================================================
    # 5. Fetch Application List & Check for Duplicates
    # ==============================================================================
    print("[INFO] Fetching application list from SOLIDserver...")

    api_url = f"{sds_host.rstrip('/')}/api/v2.0/app/application/list"
    
    headers = {
        "X-IPM-Username": b64_username,
        "X-IPM-Password": b64_password,
        "Accept": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers, verify=False)
        
        if response.status_code != 200:
            print(f"[ERROR] API call failed, HTTP Status Code: {response.status_code}")
            print(f"[ERROR] Response Details: {response.text}")
            sys.exit(1)
            
        json_data = response.json()
        
        # Verify the API itself reported success in the JSON payload
        if not json_data.get("success"):
            print("[ERROR] API returned a 200 status, but 'success' is false in the payload.")
            sys.exit(1)

        # Extract the application data array
        app_list = json_data.get("data", [])
        
        print(f"[INFO] Successfully retrieved {len(app_list)} applications. Checking for '{fqdn}'...")
        
        # Iterate through the list and look for a duplicate FQDN
        is_duplicate = False
        for app in app_list:
            if app.get("application_fqdn") == fqdn:
                is_duplicate = True
                print("-" * 50)
                print(f"[WARNING] DUPLICATE FOUND!")
                print(f"          Application FQDN '{fqdn}' already exists.")
                print(f"          App ID   : {app.get('application_id')}")
                print(f"          App Name : {app.get('application_name')}")
                print("-" * 50)
                break
                
        if not is_duplicate:
            print(f"[INFO] No duplicates found. '{fqdn}' is safe to provision.")
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from the API response.")
        print(f"[ERROR] Raw Output: {response.text}")
        sys.exit(1)
        
    # ==============================================================================
    # 6. Create the Application
    # ==============================================================================
    print("-" * 50)
    if not sds_gslbserver:
        print("[ERROR] GSLB server list cannot be empty.")
        sys.exit(1)

    print(f"\n[INFO] Provisioning application '{fqdn}' into SOLIDserver...")

    add_url = f"{sds_host.rstrip('/')}/api/v2.0/app/application/add"
    
    payload = {
        "application_fqdn": fqdn,
        "application_name": fqdn, # Using the FQDN as the App Name
        "gslbserver_list": sds_gslbserver
    }

    try:
        # We use the 'json' parameter in requests.post to automatically format the dict as JSON
        add_response = requests.post(add_url, headers=headers, json=payload, verify=False)
        
        # Checking for standard success codes (200 OK or 201 Created)
        if add_response.status_code not in [200, 201]:
            print(f"[ERROR] Application creation failed, HTTP Status Code: {add_response.status_code}")
            print(f"[ERROR] Response Details: {add_response.text}")
            sys.exit(1)
            
        add_data = add_response.json()
        
        if not add_data.get("success"):
            print("[ERROR] Application creation returned a failure in the payload.")
            print(f"[ERROR] Details: {add_data.get('messages')}")
            sys.exit(1)
            
        print(f"[INFO] Application '{fqdn}' successfully added!")
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed during application creation: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON response during creation.")
        print(f"Raw Output: {add_response.text}")
        sys.exit(1)
        
        
    # ==============================================================================
    # 7. Create the Application Pool
    # ==============================================================================
    pool_name = f"{fqdn}-pool"
    print(f"\n[INFO] Provisioning application pool '{pool_name}'...")

    pool_url = f"{sds_host.rstrip('/')}/api/v2.0/app/pool/add"
    
    pool_payload = {
        "application_fqdn": fqdn,
        "application_name": fqdn,
        "pool_lb_mode": "latency",
        "pool_name": pool_name,
        "pool_type": "ipv4",
        "pool_best_active_nodes": 2,
        "warnings": "accept"
    }

    try:
        pool_response = requests.post(pool_url, headers=headers, json=pool_payload, verify=False)
        
        if pool_response.status_code not in [200, 201]:
            print(f"[ERROR] Pool creation failed, HTTP Status Code: {pool_response.status_code}")
            print(f"[ERROR] Response Details: {pool_response.text}")
            sys.exit(1)
            
        pool_data = pool_response.json()
        
        if not pool_data.get("success"):
            print("[ERROR] Pool creation returned a failure in the payload.")
            print(f"[ERROR] Details: {pool_data.get('messages')}")
            sys.exit(1)
            
        print(f"[INFO] Application pool '{pool_name}' successfully added!")
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed during pool creation: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON response during pool creation.")
        print(f"Raw Output: {pool_response.text}")
        sys.exit(1)    
        
    # ==============================================================================
    # 8. Add Nodes to the Application Pool
    # ==============================================================================
    print(f"\n[INFO] Provisioning {len(ip_list)} nodes into pool '{pool_name}'...")
    
    # Using the API v1.0 endpoint
    node_url = f"{sds_host.rstrip('/')}/rest/app_node_add"
    
    for ip in ip_list:
        # using v1.0 API
        node_url = f"{sds_host.rstrip('/')}/rest/app_node_add?name={ip}&hostaddr={ip}&apppool_name={pool_name}&appapplication_name={fqdn}&appapplication_fqdn={fqdn}&apphealthcheck_name=tcp&apphealthcheck_freq=10&apphealthcheck_params=443%26&admin_status=1"
        
        # Pass parameters as a dictionary to 'params' - requests will URL encode them
        node_params = {
            "name": ip,
            "hostaddr": ip,
            "appapplication_name": fqdn,           # Fallback lookup value
            "appapplication_fqdn": fqdn,
            "apppool_name": pool_name,          # Fallback lookup value
            "apphealthcheck_name": "tcp",
            "apphealthcheck_freq": "10",
            "apphealthcheck_params": "443&",     # Will be automatically encoded to 443%26
            "admin_status": "1"
        }
        
        try:
            # Note: For API v1.0, we use the 'params' argument instead of 'json' to build the query string
            node_response = requests.post(node_url, headers=headers, params=node_params, verify=False)
            
            if node_response.status_code not in [200, 201]:
                print(f"[ERROR] Node creation failed for {ip}, HTTP Status Code: {node_response.status_code}")
                print(f"[ERROR] Response Details: {node_response.text}")
                sys.exit(1)
                
            # SOLIDserver v1 API typically returns a list of dictionaries. Check for errmsg.
            try:
                node_data = node_response.json()
                if isinstance(node_data, list) and len(node_data) > 0 and "errmsg" in node_data[0]:
                    print(f"[ERROR] Node creation returned a failure for {ip}.")
                    print(f"[ERROR] Details: {node_data[0].get('errmsg')}")
                    sys.exit(1)
            except json.JSONDecodeError:
                # If API v1.0 returns a plain string or non-JSON success response, we ignore the parse error
                pass
                
            print(f"[SUCCESS] Node '{ip}' successfully added to pool!")
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] HTTP Request failed during node creation for {ip}: {e}")
            sys.exit(1)
                        
    print("\n[INFO] All operations completed successfully.")

if __name__ == "__main__":
    main()
