#!/usr/bin/env bash
# Liberman fact-check reel — 1080x1920, 92s.
# Usage: build_reel.sh <2018.mp4> <2026.mp4> <cards_dir> <out.mp4>
set -euo pipefail

SRC2018="$1"; SRC2026="$2"; CARDS="$3"; OUT="$4"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FPS=30; WIDTH=1080; HEIGHT=1920
# Framing: 2026 tight, 2018 wider. Raise ZOOM_2018 if the face reads too small.
ZOOM_2026=1.4; ZOOM_2018=1.0

# --- 2026 source geometry (per brief): banner y0-253, burned subs y780-880,
#     bottom strip y1173-1279. Banner and strip are cropped away.
B_TOP=253; B_BOT=107          # pixels removed from top / bottom
SUB_Y=780; SUB_H=100          # burned-in subtitle band, masked before we re-title

# --- segment table: name  start  dur  kind  source
#     kind: v2026 | v2018 | card
SEGS=(
  "s01 0   6  v2026 -"
  "s02 0   5  card  card_01_2018"
  "s03 0   7  card  card_02_setup"
  "s04 6  12  v2026 -"
  "s05 0   9  card  card_03_cmp_personal"
  "s06 0   9  card  card_05_cmp_timeline"
  "s07 0  14  v2018 -"
  "s08 0  10  card  card_06_year_after"
  "s09 0  12  card  card_07_bottomline"
  "s10 0   8  card  card_08_sources"
)

# Freeze frames used as card backgrounds (darkened + heavily blurred).
ffmpeg -y -v error -ss 2 -i "$SRC2026" -vframes 1 "$TMP/freeze26.png"
ffmpeg -y -v error -ss 2 -i "$SRC2018" -vframes 1 "$TMP/freeze18.png"
for f in 26 18; do
  ffmpeg -y -v error -i "$TMP/freeze$f.png" -vf \
    "scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=increase,crop=${WIDTH}:${HEIGHT},gblur=sigma=48,eq=brightness=-0.34:saturation=0.55" \
    "$TMP/bg$f.png"
done

# 2026: crop banner+strip, mask burned subs, zoom 1.4, warm/saturated grade, chiron
V2026="crop=iw:ih-${B_TOP}-${B_BOT}:0:${B_TOP},\
drawbox=x=0:y=$((SUB_Y-B_TOP)):w=iw:h=${SUB_H}:color=black@1:t=fill,\
scale=${WIDTH}*${ZOOM_2026}:${HEIGHT}*${ZOOM_2026}:force_original_aspect_ratio=increase,crop=${WIDTH}:${HEIGHT},\
eq=saturation=1.18:gamma_r=1.04:gamma_b=0.96,colorbalance=rm=0.05:bm=-0.04"

# 2018: wide framing (zoom 1.0) held inside a blurred fill of the same frame,
# cool and slightly desaturated. No black bars.
V2018_FC="[0:v]split=2[b][f];\
[b]scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=increase,crop=${WIDTH}:${HEIGHT},\
gblur=sigma=42,eq=brightness=-0.30:saturation=0.5[bb];\
[f]scale=${WIDTH}*${ZOOM_2018}:-2[ff];\
[bb][ff]overlay=(W-w)/2:(H-h)/2,\
eq=saturation=0.88:gamma_b=1.05:gamma_r=0.97,colorbalance=bm=0.06:rm=-0.05,\
fps=${FPS},format=yuv420p[v]"

i=0
for row in "${SEGS[@]}"; do
  read -r name ss dur kind src <<< "$row"
  i=$((i+1)); out="$TMP/$name.mp4"
  case "$kind" in
    v2026)
      ffmpeg -y -v error -ss "$ss" -t "$dur" -i "$SRC2026" \
        -vf "${V2026},fps=${FPS},format=yuv420p" \
        -af "aresample=48000" -c:v libx264 -preset medium -crf 18 -c:a aac -ar 48000 -ac 2 "$out" ;;
    v2018)
      ffmpeg -y -v error -ss "$ss" -t "$dur" -i "$SRC2018" \
        -filter_complex "${V2018_FC}" -map "[v]" -map 0:a \
        -af "aresample=48000" -c:v libx264 -preset medium -crf 18 -c:a aac -ar 48000 -ac 2 "$out" ;;
    card)
      bg="$TMP/bg26.png"; [[ "$name" > "s07" ]] && bg="$TMP/bg18.png"
      ffmpeg -y -v error -loop 1 -t "$dur" -i "$bg" -loop 1 -t "$dur" -i "$CARDS/$src.png" \
        -f lavfi -t "$dur" -i anullsrc=r=48000:cl=stereo \
        -filter_complex "[0:v][1:v]overlay=0:0:format=auto,fps=${FPS},format=yuv420p[v]" \
        -map "[v]" -map 2:a -c:v libx264 -preset medium -crf 18 -c:a aac -ar 48000 -ac 2 "$out" ;;
  esac
  echo "file '$out'" >> "$TMP/list.txt"
done

ffmpeg -y -v error -f concat -safe 0 -i "$TMP/list.txt" -c copy "$TMP/body.mp4"

# Whooshes: one at the first cut to a card (6s), one entering the bottom line (72s).
ffmpeg -y -v error -f lavfi -t 0.5 \
  -i "anoisesrc=c=pink:r=48000:a=0.6,highpass=f=300,lowpass=f=6000,afade=t=in:d=0.06,afade=t=out:st=0.14:d=0.36,volume=1.4" \
  -ac 2 "$TMP/whoosh.wav"

ffmpeg -y -v error -i "$TMP/body.mp4" -i "$TMP/whoosh.wav" -i "$TMP/whoosh.wav" \
  -filter_complex "[1:a]adelay=6000|6000[w1];[2:a]adelay=72000|72000[w2];\
[0:a][w1][w2]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -ar 48000 -ac 2 -movflags +faststart "$OUT"

echo "done -> $OUT"
ffprobe -v error -show_entries format=duration:stream=width,height,codec_type -of default=nw=1 "$OUT"
