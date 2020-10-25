import ftplib
from time import sleep

import ftputil.session
from config import config
import os
from zipfile import ZipFile
from datetime import datetime
import re
import sys

# Debug enable
if len(sys.argv) > 1:
    debug_ftp = int(sys.argv[1])
else:
    debug_ftp = 0


# Create temp_dir
temp_dir = os.path.join(os.path.expanduser('~'), "AppData", "Local", "Temp", "ftp-backup")
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

# Create dest_dir
dest_dir = temp_dir + re.sub("/", r"\\", config["dl_dir"])
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Setting up FTP settings
session_factory = ftputil.session.session_factory(base_class=ftplib.FTP_TLS, port=config["port"],
                                                  encrypt_data_channel=True, debug_level=debug_ftp)
# Connect to FTP server
ftp_host = ftputil.FTPHost(config["host"], config["user"], config["passwd"], session_factory=session_factory)

for root, directories, files in ftp_host.walk(config["dl_dir"]):
    for filename in files:
        filepath = ftp_host.path.join(root, filename)
        if debug_ftp > 0:
            print("\nDownloading ", filepath)
        if not os.path.exists(temp_dir + re.sub("/", r"\\", os.path.split(filepath)[0])):
            os.makedirs(temp_dir + re.sub("/", r"\\", os.path.split(filepath)[0]))
        if ftp_host.download_if_newer(filepath, temp_dir + re.sub("/", r"\\", filepath)):
            if debug_ftp > 0:
                print("Success")
        else:
            if debug_ftp > 0:
                print("FAIL")

# Zip backed up files
with ZipFile(os.path.join(config["path"], "backup-" + datetime.now().strftime("%y%m%d-%H-%M-%S") + ".zip"), "w") as zipfile:
    for root, directories, files in os.walk(temp_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            zipfile.write(filepath, arcname=re.search(r'ftp-backup\\(.*)', filepath).group(1))

temp_dir_list = os.listdir(config["path"])
backup_count = len(temp_dir_list)

if backup_count - 10 > 2:
    for x in range(0, backup_count - 10, 1):
        os.remove(os.path.join(config["path"], temp_dir_list[x]))
