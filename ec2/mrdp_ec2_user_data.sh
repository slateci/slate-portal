#!/bin/bash -ex
apt-get update --assume-yes
DEBIAN_FRONTEND=noninteractive apt-get upgrade --assume-yes
timedatectl set-timezone America/Chicago
apt-get install python-setuptools python-dev build-essential python-pip unzip --assume-yes
apt-get install libssl-dev libffi-dev --assume-yes
apt-get install python-cherrypy3 --assume-yes
pip install --upgrade pip
pip install --upgrade bottle
pip install --upgrade beaker
pip install --upgrade pycrypto
pip install --upgrade pyopenssl
pip install --upgrade cherrypy
git clone https://github.com/vasv/mrdp /home/ubuntu/mrdp
mkdir /home/ubuntu/mrdp/ssl
cd /home/ubuntu/mrdp/ssl
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
-subj "/C=US/ST=Illinois/L=Chicago/O=Globus/CN=*.vasiliadis.us" \
-keyout ssl_key.pem \
-out ssl_cert.pem
chmod 400 *.pem
chown -R ubuntu:ubuntu /home/ubuntu/mrdp
cd /home/ubuntu/mrdp
sudo -u ubuntu ./mrdp_run.sh
