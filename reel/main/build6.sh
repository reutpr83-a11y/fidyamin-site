#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 plate6.py
python3 caps6.py > caps6.log
python3 datapanel6.py
rm -rf cap6; python3 render_track6.py
N=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 plate6.mov)
echo "plate frames $N"
ffmpeg -v error -i plate6.mov -an -f rawvideo -pix_fmt rgb24 - \
 | python3 composite6.py "$N" \
 | ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - \
   -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
   -color_primaries bt709 -color_trc bt709 -colorspace bt709 body6.mp4
python3 tail6.py
TF=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 tail6.mp4)
sed -i "s|TAIL = [0-9]* / 30.0|TAIL = $TF / 30.0|" audio6.py
python3 audio6.py | tail -2
python3 master6.py
