import subprocess
import sys
from sys import platform
from shutil import copyfile

def install(packages):
    for package in packages:
        subprocess.call([sys.executable, "-m", "pip", "install", package])

def getListFromFile(file, ignoreStart="#"):
    list = []
    with open(file) as handle:
        for line in handle.readlines():
            if not line.startswith(ignoreStart):
                list.append(line)
    return list


# Get dependencies
requirements = getListFromFile("setup/requirements.txt")
windows = getListFromFile("setup/windows.txt", "-r")
linux = []
mac = getListFromFile("setup/mac.txt", "-r")

# Install dependencies
install(requirements)
if platform == 'win32':
    install(windows)
if platform.startswith('linux'):
    install(linux)
if platform == 'darwin':    # MacOS
    install(mac)

# Copy config template
copyfile("./setup/config_template.ini", "config.ini")
print("Config file created")