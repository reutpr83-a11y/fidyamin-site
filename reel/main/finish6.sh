#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 tail6.py
TF=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 tail6.mp4)
sed -i "s|TAIL = [0-9]* / 30.0|TAIL = $TF / 30.0|" audio6.py
python3 audio6.py | tail -2
python3 master6.py
