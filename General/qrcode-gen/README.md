# Auto Populate GSLB Server Nodes from FQDN

[![License](https://img.shields.io/badge/License-BSD_3_Clause-lightgrey)](https://opensource.org/license/bsd-3-clause)
[![GitHub release](https://img.shields.io/badge/Github-mheidir:_SimpleScripts-blue?logo=github)](https://github.com/mheidir/SimpleScripts)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![QRCode Generator](https://img.shields.io/badge/QRCode_Generator-blue)](#)

These set of scripts helps to generate QR Codes that do not contain any link to a site full of advertisements. It will generate the QR Code based on the type of date you provide. At this moment, I am providing 3 methods:
1. Generate based on URL
2. Generate based on vCard
3. Generate based on URL and provided logo (horizontally placed across QR Code)

## Features

* **Real QR Code Generator** - No links to any advertisement site, direct towards our data
* **vCard Format Support** - Make sure to provide the correct vCard data in the following format:
```
BEGIN:VCARD
VERSION:3.0
FN:<NAME>
ORG:<COMPANY-NAME>
ADR;TYPE=WORK:<ADDRESS>
TITLE:<TITLE>
TEL;TYPE=CELL:<MOBILE-NUMBER>
EMAIL;TYPE=WORK:<EMAIL>
URL;TYPE=Digital Business Card:
URL;TYPE=Website:<COMPANY-WEBSITE>
END:VCARD
```
* **Code is Open for Improvement** - Use it, modify it and share it back to make it better
* **Image format: SVG** - Supporting this format ensure your image is not awkwardly resized. SVG allows image to be resized freely.
* **PNG as Output format** - The preferred format for QR Code

## Getting Started

### Prerequisites

List of Prerequisites:

* Python 3.10+
* Libraries: os, sys, json, qrcode, platform, PIL
* Python Virtual Environment (venv) is preferred
* vCard data or
* Image must be horizontally defined in SVG format


## Usage

Make sure to have all the required libraries

```bash
# Enter into the virtual environment
$ source ./qrcode-gen/bin/activate

# Run the application
(autofqdn)$ python3 ./qrcode-genURL.py "https://www.example.com" myqrcode.png

# Sample Output
[INFO] URL retrieved: https://www.example.com
[INFO] Framed QR Code exported successfully to 'myqrcode.png'
[INFO] Success! Saved QR code to 'myqrcode.png'.
```

## Release Notes

* This is the first release after some internal testing
* Free to use and modify to fit your needs
* Inspect code before use, and use at your own risk
* There are no backdoors or secret tunnels created
* Don't trust my code, trust your common sense (it is Open Source!!!)


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