#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 beats6.py
./build6.sh
