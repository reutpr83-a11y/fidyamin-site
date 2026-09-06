#!/usr/bin/env bash
# Liberman fact-check reel — final assembly. 1080x1920, 92.00s.
set -euo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
V2026="$1"; V2018="$2"; OUT="$3"
T="$S/work"; rm -rf "$T"; mkdir -p "$T"
FPS=30; W=1080; H=1920; SUBY=1120
FONT="/usr/share/fonts/truetype/karantina/buExpo24ccnh31GVMABxTC8f-A.ttf"
MASK="$S/mask.png"; C="$S/cards"

# 2026 (720x1280): banner y0-253 and bottom strip y1173-1279 are cropped away.
# Framing is top-anchored at zoom 1.4, which puts the burned-in subtitles
# (source y735-885) at y>=1408 in the output. A soft frosted band, keyed by
# mask.png, swallows them there; ours go in above it at the same relative
# height the originals had (~63%).
Z=1.4
PRE26="crop=720:920:0:253,scale=iw*${Z}*${H}/920:ih*${Z}*${H}/920,crop=${W}:${H}:(iw-${W})/2:0,\
eq=saturation=1.16:gamma_r=1.04:gamma_b=0.96,colorbalance=rm=0.05:bm=-0.04,fps=${FPS}"
FROST="split=2[base][soft];[soft]gblur=sigma=60,eq=brightness=-0.22:saturation=0.75[sb];\
[sb][1:v]alphamerge[sba];[base][sba]overlay=0:0"

# 2018 (1280x720): wide framing held inside a blurred fill of itself, cool grade.
Z18=1.0
PRE18="split=2[c1][c2];\
[c1]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},gblur=sigma=44,\
eq=brightness=-0.32:saturation=0.45[bg];[c2]scale=${W}*${Z18}:-2[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2,\
eq=saturation=0.86:gamma_b=1.06:gamma_r=0.96,colorbalance=bm=0.07:rm=-0.05,fps=${FPS}"

CH () { echo "drawtext=fontfile='${FONT}':text='$1':x=w-tw-46:y=54:fontsize=54:fontcolor=white@0.85:box=1:boxcolor=black@0.36:boxborderw=16"; }
ENC=(-c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -ar 48000 -ac 2)

# ---------- shot A (2026) 30.05 +6.15 : the sharpest line
ffmpeg -y -v error -ss 30.05 -t 6.15 -i "$V2026" -i "$MASK" \
 -i "$S/subs/shotA_00.png" -i "$S/subs/shotA_01.png" -i "$S/subs/shotA_02.png" \
 -filter_complex "[0:v]${PRE26},${FROST}[fr];\
[fr][2:v]overlay=0:${SUBY}:enable='between(t,0.00,2.15)'[a1];\
[a1][3:v]overlay=0:${SUBY}:enable='between(t,2.15,4.35)'[a2];\
[a2][4:v]overlay=0:${SUBY}:enable='between(t,4.95,6.15)',$(CH 2026),format=yuv420p[v]" \
 -map "[v]" -map 0:a "${ENC[@]}" "$T/01.mp4"

# ---------- shot B (2026) 11.49 +14.91 : the full quote, qualifications intact
ffmpeg -y -v error -ss 11.49 -t 14.91 -i "$V2026" -i "$MASK" \
 -i "$S/subs/shotB_00.png" -i "$S/subs/shotB_01.png" -i "$S/subs/shotB_02.png" \
 -i "$S/subs/shotB_03.png" -i "$S/subs/shotB_04.png" -i "$S/subs/shotB_05.png" \
 -i "$S/subs/shotB_06.png" \
 -filter_complex "[0:v]${PRE26},${FROST}[fr];\
[fr][2:v]overlay=0:${SUBY}:enable='between(t,0.00,2.80)'[b1];\
[b1][3:v]overlay=0:${SUBY}:enable='between(t,3.19,6.51)'[b2];\
[b2][4:v]overlay=0:${SUBY}:enable='between(t,6.75,7.86)'[b3];\
[b3][5:v]overlay=0:${SUBY}:enable='between(t,8.27,9.91)'[b4];\
[b4][6:v]overlay=0:${SUBY}:enable='between(t,10.17,11.86)'[b5];\
[b5][7:v]overlay=0:${SUBY}:enable='between(t,11.86,13.66)'[b6];\
[b6][8:v]overlay=0:${SUBY}:enable='between(t,13.66,14.91)',$(CH 2026),format=yuv420p[v]" \
 -map "[v]" -map 0:a "${ENC[@]}" "$T/04.mp4"

# ---------- shot 2018: 0.80 +12.15. The lower third "אביגדור ליברמן / שר הביטחון"
#            is on screen for the first 8s. No subtitle of ours: see README.
ffmpeg -y -v error -ss 0.80 -t 12.15 -i "$V2018" \
 -filter_complex "[0:v]${PRE18},$(CH 2018),format=yuv420p[v]" \
 -map "[v]" -map 0:a "${ENC[@]}" "$T/07.mp4"

# ---------- card backgrounds: darkened, heavily blurred freeze frames
ffmpeg -y -v error -ss 20 -i "$V2026" -vframes 1 -vf \
 "crop=720:920:0:253,scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},gblur=sigma=54,eq=brightness=-0.42:saturation=0.5" "$T/bg26.png"
ffmpeg -y -v error -ss 40 -i "$V2018" -vframes 1 -vf \
 "scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},gblur=sigma=54,eq=brightness=-0.44:saturation=0.42" "$T/bg18.png"

card () {
  ffmpeg -y -v error -loop 1 -t "$4" -i "$2" -loop 1 -t "$4" -i "$3" \
    -f lavfi -t "$4" -i anullsrc=r=48000:cl=stereo \
    -filter_complex "[0:v][1:v]overlay=0:0,fps=${FPS},format=yuv420p[v]" \
    -map "[v]" -map 2:a "${ENC[@]}" "$1"
}
card "$T/02.mp4" "$T/bg26.png" "$C/card_01_2018.png"         5.00
card "$T/03.mp4" "$T/bg26.png" "$C/card_02_setup.png"        7.00
card "$T/05.mp4" "$T/bg26.png" "$C/card_03_cmp_personal.png" 9.00
card "$T/06.mp4" "$T/bg26.png" "$C/card_05_cmp_timeline.png" 9.00
card "$T/08.mp4" "$T/bg18.png" "$C/card_06_year_after.png"  10.00
card "$T/09.mp4" "$T/bg18.png" "$C/card_07_bottomline.png"  11.00
card "$T/10.mp4" "$T/bg18.png" "$C/card_08_sources.png"      7.79

for f in 01 02 03 04 05 06 07 08 09 10; do echo "file '$T/$f.mp4'"; done > "$T/list.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$T/list.txt" -c copy "$T/body.mp4"

# ---------- two whooshes: first cut to a card (6.15s), entry to the bottom line (73.21s)
ffmpeg -y -v error -f lavfi -t 0.55 \
 -i "anoisesrc=c=pink:r=48000:a=0.55,highpass=f=260,lowpass=f=5200,afade=t=in:d=0.07,afade=t=out:st=0.16:d=0.39,volume=1.25" \
 -ac 2 "$T/whoosh.wav"
ffmpeg -y -v error -i "$T/body.mp4" -i "$T/whoosh.wav" -i "$T/whoosh.wav" \
 -filter_complex "[1:a]adelay=6150|6150[w1];[2:a]adelay=73210|73210[w2];\
[0:a][w1][w2]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.94,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$OUT"

echo "--- delivered: $OUT"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 "$OUT"
