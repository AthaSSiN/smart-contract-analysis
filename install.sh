#!/bin/bash

pip3 install -r requirements.txt
docker pull mythril/myth
docker pull trailofbits/eth-security-toolbox
docker build -t est2
