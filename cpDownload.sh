#!/bin/bash

downloadDir="/home/jails/home/sftp/Download/"

sudo rsync --progress $1 $downloadDir

printf "\nSetting file access rights...\n"
sudo chown -R sftpuser:sftpusers $downloadDir

printf "Transfer completed!\n"
