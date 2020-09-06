#!/bin/bash
set -euo pipefail

# use nvm for node version control
echo "install nvm"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash

export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

echo "install node"
nvm install v12.18.3 && nvm use v12.18.3

echo "install nginx self signed cert"
sudo mkdir /var/lib/sslcerts
pushd /var/lib/sslcerts
sudo openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -subj '/CN=3.134.38.206'
sudo chmod 0644 cert.pem
sudo chmod 0644 key.pem
popd


