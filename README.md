# SimpleScripts

Contains a compilation of shell scripts used in Linux-based operating systems and product vendor specific separated into its own directories. Each of the script information is listed below with explanation to help understand the source code. Some codes are forked or located from web forums which are referenced as the source.

The list is dynamic and may change without notice. No restrictions on usage, but do help to improve if you can.


## General

Contains generic shell scripts (mostly in BASH) for use in GNU Linux Ubuntu/Debian-based operating systems.
List of Scripts:
- **checkExpiredUsers.sh**
To list down all user accounts that has already expired
- **useradd_expire_day.sh**
To create a new user account specifying the expiration date after N-days
- **useradd_expire.sh**
To create a new user account specifying the date when the account should expire


## BCN

Contains BlueCat specific shell scripts. These scripts were created in the year between 2015-2019 and with a specific use case. Listed here for my personal reference.
List of Scripts:
- **cpDownload.sh**
An rsync script to download a file to a specified destination hard coded in the script. Probably used to copy a local or remote folder to the BlueCat BAM/DDS.
- **rpz-download.sh**
This script was used to download blacklisted domains from KomInfo Indonesia and compile it into a BIND DB file ready for deployment as the Primary DNS for Response Policy Zones (RPZ or DNS Firewall).


## EIP

Contains **EfficientIP** specific shell scripts. These scripts were created in the year between 2020 till current. (*The scripts are pending compilation and will be uploaded soon*)


## LICENSE

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see  [www.gnu.org/licenses/](https://www.gnu.org/licenses/).

## CONTRIBUTION

You are free to contribute on improvements or suggestions.

## CONTACT

For bug reports or feature requests please refer to the tracking system at  [Github](https://github.com/mheidir/BASHScripts/issues). Support is voluntary and not a commitment to fix.
You're always welcome to send a message to the project admin: mheidir(at)systemx(dot)sg
