import ftplib
from ftplib import FTP
from config import config

print("Creating FTP Object")
ftp = FTP()
print("Connecting...")
ftp.connect(config["host2"], config["port2"])
print("Logging in...")
ftp.login(config["user2"], config["passwd2"])
print("Listing...")
ftp.retrlines('LIST')

files = []

try:
    files = ftp.nlst()
except ftplib.error_perm as resp:
    if str(resp) == "550 No files found":
        print("No files in this directory")
    else:
        raise

for f in files:
    print(f)


