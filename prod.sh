#!/bin/bash

while :; do
    ./run.py

    if [[ $? != 42 ]]; then
        break
    else
        echo "Reloading all and restarting"
        git pull
    fi
done
