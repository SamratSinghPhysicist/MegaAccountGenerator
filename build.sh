#!/usr/bin/env bash
# Exit on error
set -o errexit

# Add Chrome's repository key
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Add Chrome's repository
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update package list and install Chrome
apt-get update
apt-get install -y google-chrome-stable

# Create symlink to chrome binary
ln -sf /usr/bin/google-chrome-stable /usr/bin/chrome

# Install Python dependencies
pip install -r requirements.txt

# Print Chrome version for verification
google-chrome-stable --version