#!/usr/bin/env bash
set -o errexit

# Update package lists
apt-get update

# Install Chrome dependencies
apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    hicolor-icon-theme \
    libcanberra-gtk* \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    libpango1.0-0 \
    libpulse0 \
    libv4l-0 \
    fonts-symbola \
    unzip \
    wget \
    xdg-utils

# Install Chromium
apt-get install -y chromium-browser

# Verify installations
chromium-browser --version

# Install Python dependencies
pip install -r requirements.txt