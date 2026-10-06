#!/usr/bin/env bash

# setup steps that need to be run as root

if (( $EUID != 0 )); then
    echo "Must run as sudo or root"
    exit 1
fi

QUIET="/dev/null"

# apt update
echo "Updating and upgrading apt"
sudo apt update &> $QUIET && apt upgrade -y &> $QUIET

# Python
echo "Installing python..."
sudo apt install python3 python3-pip pythonpy -y  &> $QUIET
echo "Installed python: $(python3 --version)" \
    && echo "Installed pip: $(pip --version)" \
    || echo "Failed to install python" >&2

# NodeJS
echo "Installing NodeJS..."
sudo apt install nodejs npm -y  &> $QUIET
echo "Installed node: $(node --version)" \
    && echo "Installed npm: $(npm --version)" \
    || echo "Failed to install nodejs" >&2

# jdk for react native
echo "Installing jdk-17..."
sudo apt install openjdk-17-jdk -y  &> $QUIET
echo "Installed jdk: $(java --version)" \
    || echo "Failed to install jdk-17" >&2

# manual setup
sudo chmod +x setup2.sh

echo
echo
echo "DO THESE STEPS TO FINISH SETUP!!" 

echo
echo -e "Connect Docker Desktop at:\
    \n\tSettings > Resources > WSL Integration \
    \n\tToggle this WSL distro ON\n\tApply & restart"

echo
echo "run 'code .' and wait for WSL to connect to VSCode, then run setup2.sh as user"
