import subprocess
import sys
from sys import platform

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
requirements = getListFromFile("requirements/requirements.txt")
windows = getListFromFile("requirements/windows.txt", "-r")
linux = []
mac = getListFromFile("requirements/mac.txt", "-r")

# Install dependencies
install(requirements)
if platform.startswith('win'):
    install(windows)
if platform.startswith('linux'):
    install(linux)
if platform == 'darwin':    # MacOS
    install(mac)
