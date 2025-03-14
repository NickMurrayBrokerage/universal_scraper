#!/bin/sh
echo "Installing build tools..."
apt-get update && apt-get install -y wget unzip
echo "Installing Chrome..."
wget -q -O /tmp/chrome-linux.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-linux64.zip
unzip -q /tmp/chrome-linux.zip -d /tmp
chmod +x /tmp/chrome-linux64/chrome
echo "Chrome installed at /tmp/chrome-linux64/chrome"
pip install -r requirements.txt