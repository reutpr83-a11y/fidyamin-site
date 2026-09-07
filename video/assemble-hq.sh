#!/usr/bin/env bash
# The same edit as append-endcard.sh, without re-encoding what did not change.
#
# Every edit sits in the last stretch of these films: the dropped word, the
# graded tail, the card. So the part before the first edit is copied straight
# out of the source and keeps the exact bytes it had, taking no second
# generation of compression, and only the tail is encoded. On a 93s film with
# its first edit at 77s that is 83 percent of the running time left untouched.
#
# The copy has to end on a keyframe, or the frames after the split decode
# against a reference that is no longer in the file, so the split lands on the
# last keyframe before the first edit and the encoded tail picks up there.
#
#   HEADEND  first edited moment in source time (required)
#   CUT      where the speech ends and the card begins
#   DROP     "start-end", a span lifted out, edges inside pauses
#   GRADE    filter chain for a tail lit differently, in source time
#   JOINX    dissolve over the drop join, default 0.12
#   TRANS    dissolve into the card, default 0.5
#   AFADE    audio fade at the end, default 1.6
#   PREGRAPH a filter graph fragment taking [0:v] and producing [src], for
#            work that needs more than a linear chain. Used to paint over a
#            wrong letter in a burned in caption by copying clean background
#            from the same frame. Only useful for edits that fall inside the
#            encoded tail; anything earlier is in the copied part.
#   CRF      quality of the encoded tail only, default 17
set -euo pipefail
cd "$(dirname "$0")"

IN="${1:?usage: assemble-hq.sh <cut.mp4>}"
CARD="out/endcard.mp4"
OUT="${OUT:-out/hq.mp4}"
TRANS="${TRANS:-0.5}"; AFADE="${AFADE:-1.6}"; CRF="${CRF:-17}"
HEADEND="${HEADEND:?set HEADEND to the first edited moment}"
[ -f "$CARD" ] || { echo "missing $CARD, run ./build-endcard.sh first" >&2; exit 1; }

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
CUT="${CUT:?set CUT}"; CARD_DUR=$(dur "$CARD")

D0="$CUT"; D1="$CUT"; DROPLEN=0; JOINX="${JOINX:-0.12}"
if [ -n "${DROP:-}" ]; then
  D0="${DROP%%-*}"; D1="${DROP##*-}"
  DROPLEN=$(awk -v a="$D0" -v b="$D1" 'BEGIN{printf "%.3f", b-a}')
else
  JOINX=0
fi

KF=$(ffprobe -v error -select_streams v -skip_frame nokey \
       -show_entries frame=pts_time -of csv=p=0 "$IN" \
     | tr -d ',' | awk -v h="$HEADEND" '$1 <= h {k=$1} END {printf "%.3f", k}')
awk -v k="$KF" 'BEGIN{if(k<=0){print "no keyframe before the first edit" > "/dev/stderr"; exit 1}}'

TAILBODY=$(awk -v k="$KF" -v a="$D0" -v b="$D1" -v c="$CUT" -v j="$JOINX" \
  'BEGIN{printf "%.3f", (a-k)+(c-b)-j}')
TOTAL=$(awk -v t="$TAILBODY" -v k="$CARD_DUR" -v x="$TRANS" 'BEGIN{printf "%.3f", t+k-x}')
JOFF=$(awk -v a="$D0" -v k="$KF" -v j="$JOINX" 'BEGIN{printf "%.3f", a-k-j}')
XSTART=$(awk -v t="$TAILBODY" -v x="$TRANS" 'BEGIN{printf "%.3f", t-x}')
ASTART=$(awk -v T="$TOTAL" -v f="$AFADE" 'BEGIN{printf "%.3f", (T-f<0?0:T-f)}')
echo "copy 0 to ${KF}s · encode ${KF}s onward · tail ${TOTAL}s · total $(awk -v k="$KF" -v t="$TOTAL" 'BEGIN{printf "%.2f", k+t}')s"

ffmpeg -nostdin -y -v error -i "$IN" -t "$KF" -c copy -avoid_negative_ts make_zero "$WORK/head.mp4"

ffmpeg -nostdin -y -v warning -stats -i "$IN" -i "$CARD" -filter_complex "
  ${PREGRAPH:-[0:v]null[src]};
  [src]${GRADE:+${GRADE},}split=2[s0][s1];
  [s0]trim=${KF}:${D0},setpts=PTS-STARTPTS[p0];
  [s1]trim=${D1}:${CUT},setpts=PTS-STARTPTS[p1];
  [p0][p1]xfade=transition=fade:duration=${JOINX}:offset=${JOFF},format=yuv420p,fps=30[v0];
  [1:v]setpts=PTS-STARTPTS,format=yuv420p,fps=30[v1];
  [v0][v1]xfade=transition=fade:duration=${TRANS}:offset=${XSTART}[v];
  [0:a]asplit=2[q0][q1];
  [q0]atrim=${KF}:${D0},asetpts=PTS-STARTPTS[r0];
  [q1]atrim=${D1},asetpts=PTS-STARTPTS[r1];
  [r0][r1]acrossfade=d=${JOINX}:c1=tri:c2=tri,
       apad=whole_dur=${TOTAL},afade=t=out:st=${ASTART}:d=${AFADE}[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -profile:v high -level 4.2 -preset slow -crf "$CRF" \
  -maxrate 16M -bufsize 24M -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 256k -ar 48000 -t "$TOTAL" "$WORK/tail.mp4"

printf "file '%s'\nfile '%s'\n" "$WORK/head.mp4" "$WORK/tail.mp4" > "$WORK/list.txt"
ffmpeg -nostdin -y -v error -f concat -safe 0 -i "$WORK/list.txt" -c copy -movflags +faststart "$OUT"
echo "wrote $OUT"
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=noprint_wrappers=1 "$OUT"
