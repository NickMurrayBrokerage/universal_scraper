#!/bin/bash
export TERM=dumb
apt-get update
apt-get install -y google-chrome-stable
pip install -r requirements.txt