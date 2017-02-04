#!/bin/bash

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
IP=192.168.7.2

cd $FRANKFURTER_DIR

if ! ls build/frankfurter-update-* 1> /dev/null 2>&1; then
    make create_update
fi

# Disable host fingerprinting
OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
ssh $OPTIONS ubuntu@$IP 'rm -f ~/updates/*.tar.gz* && rm -rf ~/updates/tmp'
scp $OPTIONS build/* ubuntu@$IP:~/updates/
ssh -t $OPTIONS ubuntu@$IP 'sudo /home/ubuntu/bin/update.sh && sudo systemctl restart runtime.service'
