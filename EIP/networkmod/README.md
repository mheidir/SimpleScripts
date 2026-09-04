# Auto Populate GSLB Server Nodes from FQDN

[![License](https://img.shields.io/badge/License-BSD_3_Clause-lightgrey)](https://opensource.org/license/bsd-3-clause)
[![GitHub release](https://img.shields.io/badge/Github-mheidir:_SimpleScripts-blue?logo=github)](https://github.com/mheidir/SimpleScripts)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![EfficientIP SOLIDserver](https://img.shields.io/badge/EfficientIP:_SOLIDserver:_IPAM_DNS_DHCP-blue)](#)

These compilation of scripts helps operational teams to update the subnet gateway IP, Domain Name Server option on DHCP and updating the DHCP Range.

## Features

* **networkpull.py** - Require a CSV file containing 2 columns, Start = Network IP Address, Space = Space name defined in the SOLIDserver. Output filename is fixed: network_compiled.csv. The output file can then be used to make changes to the gateway IP, DNS IP and DHCP Range for updating using the other individual scripts.
* **network_updategw.py** - Reads the "network_compiled.csv" file for the 'option routers' which are the gateway IP address. Performs a check against the currently configured one and only update when there is a difference.
* **network_updatedns.py** - Reads the "network_compiled.csv" file for the 'option domain-name-servers' which contains the DHCP Option 6 (domain-name-servers), checks for differences configured in the SOLIDserver and updates if there is a mismatch.
* **network_updaterange.py** - Reads the "network_compiled.csv" file for the 'dhcprange_start_addr' and 'dhcprange_end_addr', compares with the one configured in the SOLIDserver and updates if there is a mismatch.

## Getting Started

### Prerequisites

List of Prerequisites:

* SOLIDserver v8.4.x or v9.1.x or later
* Python 3.10+
* Libraries: sys, csv, socket, base64, json, urllib3, requests, ipaddress, time
* Python Virtual Environment (venv) is preferred
### Preparation

Step-by-step instructions to get a development environment up and running.

1. **Clone the repository**
   ```bash
   $ git clone https://github.com/mheidir/SimpleScripts
   $ cd SimpleScripts/EIP/networkmod
   ```

2. **Install dependencies**
   ```bash
   $ python3 -m venv networkmod
   ```

3. **Configure environment variables**
   ```bash
   $ vi sds.conf

   SDSHOST="https://192.168.x.x"
   SDSUSERNAME="xxxx"
   SDSPASSWORD="xxxx"
   ```

## Usage

Make sure to provide the correct host and credentials for the script to connect to the SOLIDserver via API.
The script will check the connectivity after the configuration file is read.

```bash
# Enter into the virtual environment
$ source ./networkmod/bin/activate

# Pull existing data comprising of Gateway, DHCP Range and Domain Name Servers
(networkmod)$ python3 ./networkpull.py network_list.csv

# Edit the output file: network_compiled.csv
# Modifying the specific options for example: 'option routers', 'option domain-name-servers', 'dhcprange_start_addr', 'dhcprange_end_addr'

# Update the Gateway IP
(networkmod)$ python3 ./network_updategw.py network_compiled.csv

# Update the Domain Name Servers IP
(networkmod)$ python3 ./network_updatedns.py network_compiled.csv

# Update the DHCP Range
(networkmod)$ python3 ./network_updaterange.py network_compiled.csv

```

## Release Notes

* This release was created to showcase the capablity of leveraging SOLIDserver API to simplify the updating of configuration across multiple subnets and services


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