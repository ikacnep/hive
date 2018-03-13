#!/bin/sh

# /dev/shm — это рамдиск
HIVE_DATABASE_DIR=/dev/shm python3 -m unittest discover --pattern '*Tests.py' "$@"
