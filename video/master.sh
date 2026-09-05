#!/usr/bin/env bash
# Master: two pass loudness on the score, then mux with the picture.
# Target is -14 LUFS integrated and -1 dBTP, which is what Instagram
# normalises around and leaves the file untouched.
set -euo pipefail
cd "$(dirname "$0")"

FF="${FFMPEG:-/tmp/ffdl/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2}"
OUT=out
SCORE=$OUT/score.wav
PIC=$OUT/video-only.mp4
FINAL=$OUT/harish-budget-reels-1080x1920.mp4

I=-14; TP=-1.0; LRA=9

echo "== pass 1, measuring"
MEASURE=$("$FF" -hide_banner -nostats -i "$SCORE" \
  -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:print_format=json" -f null - 2>&1 \
  | sed -n '/^{/,/^}/p')

get(){ echo "$MEASURE" | grep "\"$1\"" | sed 's/.*: *"\([^"]*\)".*/\1/'; }
MI=$(get input_i); MTP=$(get input_tp); MLRA=$(get input_lra)
MTH=$(get input_thresh); MOFF=$(get target_offset)
echo "   measured  I=$MI  TP=$MTP  LRA=$MLRA"

echo "== pass 2, applying and muxing"
"$FF" -hide_banner -loglevel error -y \
  -i "$PIC" -i "$SCORE" \
  -filter_complex "[1:a]loudnorm=I=$I:TP=$TP:LRA=$LRA:measured_I=$MI:measured_TP=$MTP:measured_LRA=$MLRA:measured_thresh=$MTH:offset=$MOFF:linear=true:print_format=summary[a]" \
  -map 0:v -map "[a]" -shortest \
  -c:v copy \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  "$FINAL"

echo "== result"
"$FF" -hide_banner -i "$FINAL" 2>&1 | grep -E "Duration|Stream #"
"$FF" -hide_banner -nostats -i "$FINAL" -af ebur128=peak=true -f null - 2>&1 \
  | grep -A6 "Integrated loudness" | head -8
ls -lh "$FINAL"
