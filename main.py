import ftplib
import ftputil.session
from config import config
import os
from zipfile import ZipFile
from datetime import datetime
import re


# Recursively calculates the total size of the given directory**
def get_size(path, host):
    total_bytes = 0
    for filename in host.listdir(path):
        filepath = host.path.join(path, filename)
        if host.path.isfile(filepath):
            total_bytes += host.path.getsize(filepath)
        elif host.path.isdir(filepath):
            total_bytes += get_size(filepath, host)
    return total_bytes


# Recursively downloads files from a given directory and stores them in the user's temp folder
def download(path, host, temp):
    for filename in host.listdir(path):
        if host.path.isfile(host.path.join(path, filename)):
            print("\nFile: ", host.path.join(path, filename))
            if host.download_if_newer(host.path.join(path, filename), os.path.join(temp, filename)):
                print("| ", filename, " | ", " Download Successful")
            else:
                print("| ", filename, " | ", " Download Failed ")
        elif host.path.isdir(host.path.join(path, filename)):
            if not filename.startswith("@"):
                new_temp = os.path.join(temp, filename)
                print("\nDirectory: ", host.path.join(path, filename))
                if not os.path.exists(new_temp):
                    os.mkdir(new_temp)
                download(host.path.join(path, filename), host, new_temp)
    return True


# Takes in a list of paths and downloads each file to the user's temp folder, folder structure is retained
def download_from_paths(host, temp):
    with open(os.path.join(temp_dir, "files.txt"), 'r') as file:
        for filepath in file.read().splitlines():
            print("Downloading ", filepath)
            if not os.path.exists(temp + re.sub("/", r"\\", os.path.split(filepath)[0])):
                os.makedirs(temp + re.sub("/", r"\\", os.path.split(filepath)[0]))
            if host.download_if_newer(filepath, temp + re.sub("/", r"\\", filepath)):
                print("Success")
            else:
                print("FAIL")


# Returns absolute directory for all files in given path
def get_paths(path):
    file_paths = []
    for root, directories, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


# Returns absolute directory for all files in given ftp remote path
def get_remote_paths(path, host):
    file_paths = []
    for root, directories, files in host.walk(path):
        for filename in files:
            filepath = host.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


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
                                                  encrypt_data_channel=True, debug_level=0)
# Connect to FTP server
ftp_host = ftputil.FTPHost(config["host"], config["user"], config["passwd"], session_factory=session_factory)

with open(os.path.join(temp_dir, "files.txt"), 'w') as f:
    for path in get_remote_paths(dest_dir, ftp_host):
        f.write(path + "\n")

download_from_paths(ftp_host, temp_dir)

# Zip backed up files
with ZipFile(os.path.join(config["path"], "backup-" + datetime.now().strftime("%y%m%d-%H-%M-%S") + ".zip"), "w") as zipfile:
    for file in get_paths(temp_dir):
        zipfile.write(file, arcname=re.search(r'ftp-backup\\(.*)', file).group(1))
