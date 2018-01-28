#!/bin/sh

python3 -m unittest discover --pattern '*Tests.py' "$@"
