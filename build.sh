#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
apt-get update -y
apt-get install -y wget gnupg2 unzip

# Install Google Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update -y
apt-get install -y google-chrome-stable

# Print Chrome version
google-chrome --version

# Install Python dependencies
pip install -r requirements.txt