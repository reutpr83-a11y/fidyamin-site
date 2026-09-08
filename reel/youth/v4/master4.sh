#!/bin/sh
set -e
cd "$(dirname "$0")"
# body + held tail, then a half second dissolve into the card. Nothing in the
# reel is a hard cut: the beats dissolve, the tail is frame continuous with the
# last beat, and the card fades up on silence.
ffmpeg -y -v error \
  -i body4.mp4 -i tail4.mp4 -i endcard4.mp4 -i audio4.wav \
  -filter_complex "\
[0:v]fps=30,settb=1/15360[b0];[1:v]fps=30,settb=1/15360[b1];[2:v]fps=30,settb=1/15360[b2];[b0][b1]concat=n=2:v=1:a=0,settb=1/15360[bd];\
[bd][b2]xfade=transition=fade:duration=0.50:offset=37.4333[v];\
[3:a]afade=t=out:st=37.20:d=0.70,apad,atrim=0:41.4333,asetpts=N/SR/TB[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart \
  youth-reel-v4.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 youth-reel-v4.mp4
