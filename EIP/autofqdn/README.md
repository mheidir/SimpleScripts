# Auto Populate GSLB Server Nodes from FQDN

[![License](https://img.shields.io/badge/License-BSD_3_Clause-lightgrey)](https://opensource.org/license/bsd-3-clause)
[![GitHub release](https://img.shields.io/badge/Github-mheidir:_SimpleScripts-blue?logo=github)](https://github.com/mheidir/SimpleScripts)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![EfficientIP SOLIDserver](https://img.shields.io/badge/EfficientIP:_SOLIDserver:_GSLB-blue)](#)

This script auto-populates server nodes into the SOLIDserver GSLB configuration when a fully qualified domain name (FQDN) is supplied. It is designed for proof-of-concept purposes and can be modified to meet specific business case.

## Features

* **FQDN Lookup** - Automatically locate the A records assigned to the FQDN
* **Specify DNS Server** - Look up the A records resolved by the specific DNS server instead of using the host machine DNS server
* **APIv1 or APIv2** - APIv2 is simpler but specific health check settings do not work. Use APIv1 instead.
* **Python Modules** - sys, socket, base64, json, urllib3, requests, dns.resolver

## Getting Started

### Prerequisites

List of Prerequisites:

* SOLIDserver v8.4.x or v9.1.x or later
* Python 3.10+
* Libraries: sys, socket, base64, json, urllib3, requests, dns.resolver
* Python Virtual Environment (venv) is preferred

### Preparation

Step-by-step instructions to get a development environment up and running.

1. **Clone the repository**
   ```bash
   $ git clone https://github.com/mheidir/SimpleScripts
   $ cd SimpleScripts/EIP/autofqdn
   ```

2. **Install dependencies**
   ```bash
   $ python3 -m venv autofqdn
   ```

3. **Configure environment variables**
   ```bash
   $ vi sds.conf

   SDSHOST="https://192.168.x.x"
   SDSUSERNAME="xxxx"
   SDSPASSWORD="xxxx"
   GSLBSERVER="xxxxx"

   ```

## Usage

Make sure to provide the correct host and credentials for the script to connect to the SOLIDserver via API.
The script will check the connectivity after the DNS lookup is performed.

```bash
# Enter into the virtual environment
$ source ./autofqdn/bin/activate

# Run the application
(autofqdn)$ python3 ./autofqdn_v1.py www.example.com

# Sample Output
Enter the DNS server IP to query (leave blank to use system assigned DNS): 192.168.10.12
[INFO] Performing A record lookup for 'www.google.com' via DNS server 192.168.10.12...
[INFO] Found 8 A record(s):
 - 142.251.155.119
 - 142.251.153.119
 - 142.251.157.119
 - 142.251.151.119
 - 142.251.150.119
 - 142.251.152.119
 - 142.251.154.119
 - 142.251.156.119
[INFO] Testing API connection to SOLIDserver...
[INFO] Success: API returned 200 OK.
[INFO] Fetching application list from SOLIDserver...
[INFO] Successfully retrieved 4 applications. Checking for 'www.google.com'...
[INFO] No duplicates found. 'www.google.com' is safe to provision.
--------------------------------------------------

[INFO] Provisioning application 'www.google.com' into SOLIDserver...
[INFO] Application 'www.google.com' successfully added!

[INFO] Provisioning application pool 'www.google.com-pool'...
[INFO] Application pool 'www.google.com-pool' successfully added!

[INFO] Provisioning 8 nodes into pool 'www.google.com-pool'...
[SUCCESS] Node '142.251.155.119' successfully added to pool!
[SUCCESS] Node '142.251.153.119' successfully added to pool!
[SUCCESS] Node '142.251.157.119' successfully added to pool!
[SUCCESS] Node '142.251.151.119' successfully added to pool!
[SUCCESS] Node '142.251.150.119' successfully added to pool!
[SUCCESS] Node '142.251.152.119' successfully added to pool!
[SUCCESS] Node '142.251.154.119' successfully added to pool!
[SUCCESS] Node '142.251.156.119' successfully added to pool!

[INFO] All operations completed successfully.

```

## Release Notes

* APIv1: Using this script sets the health check frequency = 10 and health check port = TCP/443. This is hard coded in the script. You can modify this on lines 328 and 329.
* APIv2: Using this script uses the default health check frequency = 30 with no health check port defined. You have to manually set it. This is a known issue and has been raised with Technical Support.


## Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the **BSD 3-Clause License**. 

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