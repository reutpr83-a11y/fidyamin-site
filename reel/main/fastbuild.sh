#!/bin/sh
# The whole reel, with the composite split across the four cores.
set -e
cd "$(dirname "$0")"
T0=$(date +%s)
python3 beats6.py
python3 plate6.py
python3 caps6.py > caps6.log; head -1 caps6.log
python3 datapanel6.py
rm -rf cap6; python3 render_track6.py
N=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 plate6.mov)
echo "plate frames $N"

# four workers, each decoding its own slice of the plate and encoding its own
# chunk. REEL_FRAMES keeps the push in computed against the whole reel and not
# against the chunk, so the zoom is continuous across the joins.
export REEL_FRAMES=$N
W=4; CH=$(( (N + W - 1) / W ))
rm -f part*.mp4 parts.txt
k=0
while [ $k -lt $W ]; do
  S=$(( k * CH )); n=$(( N - S )); [ $n -gt $CH ] && n=$CH
  if [ $n -gt 0 ]; then
    ( ffmpeg -v error -ss $(python3 -c "print($S/30.0)") -i plate6.mov -frames:v $n -an \
        -f rawvideo -pix_fmt rgb24 - \
      | python3 composite6.py $n $S \
      | ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - \
        -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p \
        -x264-params keyint=30:min-keyint=30:scenecut=0 \
        -color_primaries bt709 -color_trc bt709 -colorspace bt709 part$k.mp4 ) &
    echo "file 'part$k.mp4'" >> parts.txt
  fi
  k=$(( k + 1 ))
done
wait
ffmpeg -y -v error -f concat -safe 0 -i parts.txt -c copy body6.mp4
GOT=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 body6.mp4)
echo "body frames $GOT of $N"
[ "$GOT" = "$N" ] || { echo "FRAME COUNT MISMATCH"; exit 1; }

python3 tail6.py
TF=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 tail6.mp4)
sed -i "s|TAIL = [0-9]* / 30.0|TAIL = $TF / 30.0|" audio6.py
python3 audio6.py | tail -2
python3 master6.py
echo "total $(( $(date +%s) - T0 ))s"
