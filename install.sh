#!/bin/bash

pip install -r requirements.txt
docker pull mythril/myth
docker pull trailofbits/eth-security-toolbox
docker build -t est2 .
