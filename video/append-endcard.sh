#!/usr/bin/env bash
# Replaces the held last frame of a presenter cut with the end card.
#
#   ./append-endcard.sh video/out/harish-budget-presenter-1080x1920.mp4
#
# Finds where the picture stops moving, cuts there, and dissolves into
# out/endcard.mp4. The soundtrack keeps running under the card and fades
# out, so the film does not end on a hard audio cut.
#
# Override the automatic detection when the eye disagrees with the filter:
#   CUT=41.8 ./append-endcard.sh in.mp4
#
# Env: CUT (seconds), TRANS (dissolve seconds, 0 for a straight cut),
#      AFADE (audio fade seconds), CRF (quality, lower is bigger), OUT,
#      DROP ("start-end", a span lifted out of the middle),
#      GRADE (a filter chain applied to the source before the card, for
#      matching a tail shot that was lit differently, e.g.
#      GRADE="colorchannelmixer=rr=.96:gg=.92:bb=.88:enable='gte(t,83.5)'").
#
# Quality rather than a fixed bitrate: render.js targets 14M because flat
# typography needs it, but that triples the size of camera footage for no
# visible gain. CRF 19 lands close to the source and stays there whatever
# the clip length.
set -euo pipefail
cd "$(dirname "$0")"

IN="${1:?usage: append-endcard.sh <presenter-cut.mp4>}"
CARD="out/endcard.mp4"
OUT="${OUT:-out/presenter-with-endcard.mp4}"
TRANS="${TRANS:-0.5}"
AFADE="${AFADE:-1.6}"

[ -f "$CARD" ] || { echo "missing $CARD, run ./build-endcard.sh first" >&2; exit 1; }

dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
SRC_DUR=$(dur "$IN")
CARD_DUR=$(dur "$CARD")

# ---- where does the picture stop moving ----------------------------------
# freeze-probe.py reports what it found and nominates a cut only when the
# evidence is unambiguous. When it declines, it says why, and the fix is to
# look at the frames and pass CUT= rather than to loosen the threshold until
# something comes out.
if [ -z "${CUT:-}" ]; then
  if CUT=$(python3 freeze-probe.py "$IN" "${FREEZE_DB:--45}"); then
    echo "frozen tail from ${CUT}s to the end, cutting there"
  else
    echo "no cut nominated. Re-run with CUT=<seconds> once you have picked the frame." >&2
    exit 1
  fi
fi

# A hand placed CUT still has to land inside the clip.
awk -v c="$CUT" -v s="$SRC_DUR" 'BEGIN{if(c<=0||c>s){print "CUT "c"s is outside 0 to "s"s" > "/dev/stderr"; exit 1}}'

# DROP="start-end" lifts one span out of the middle, for a word or a
# stumble that has to go. Both edges should sit inside a pause: find them
# with silencedetect rather than by eye, or the cut clips a syllable.
# GRADE is applied before the split so its enable= times stay in source
# time and do not have to be shifted by the length of the drop.
D0="${CUT}"; D1="${CUT}"; DROPLEN=0
if [ -n "${DROP:-}" ]; then
  D0="${DROP%%-*}"; D1="${DROP##*-}"
  DROPLEN=$(awk -v a="$D0" -v b="$D1" 'BEGIN{printf "%.3f", b-a}')
  awk -v a="$D0" -v b="$D1" -v c="$CUT" 'BEGIN{if(!(0<a && a<b && b<c)){print "DROP "a"-"b" is not inside 0.."c > "/dev/stderr"; exit 1}}'
  echo "dropping ${DROPLEN}s from ${D0}s to ${D1}s"
fi

# The two halves are dissolved rather than butted together. Both edges sit
# in a pause so the sound would cut cleanly either way, but the camera
# drifts a little between them and a straight join shows as a jump. 120ms
# is the same short fade the caption spec allows, short enough that it
# reads as a cut and long enough to hide the drift. Audio crossfades over
# the same span so the two stay in step.
JOINX="${JOINX:-0.12}"
[ -n "${DROP:-}" ] || JOINX=0
JOFF=$(awk -v a="$D0" -v j="$JOINX" 'BEGIN{printf "%.3f", a-j}')
BODY=$(awk -v c="$CUT" -v d="$DROPLEN" -v j="$JOINX" 'BEGIN{printf "%.3f", c-d-j}')
TOTAL=$(awk -v b="$BODY" -v k="$CARD_DUR" -v t="$TRANS" 'BEGIN{printf "%.3f", b+k-t}')
XSTART=$(awk -v b="$BODY" -v t="$TRANS" 'BEGIN{printf "%.3f", b-t}')
ASTART=$(awk -v T="$TOTAL" -v f="$AFADE" 'BEGIN{printf "%.3f", (T-f<0?0:T-f)}')
echo "body ${BODY}s + card ${CARD_DUR}s - dissolve ${TRANS}s = ${TOTAL}s"

# The source may be shorter than the finished film once the frozen tail is
# gone, so the audio is padded with silence before the fade is applied.
ffmpeg -nostdin -y -v warning -stats -i "$IN" -i "$CARD" -filter_complex "
  [0:v]${GRADE:+${GRADE},}split=2[s0][s1];
  [s0]trim=0:${D0},setpts=PTS-STARTPTS[p0];
  [s1]trim=${D1}:${CUT},setpts=PTS-STARTPTS[p1];
  [p0][p1]xfade=transition=fade:duration=${JOINX}:offset=${JOFF},format=yuv420p,fps=30[v0];
  [1:v]setpts=PTS-STARTPTS,format=yuv420p,fps=30[v1];
  [v0][v1]xfade=transition=fade:duration=${TRANS}:offset=${XSTART}[v];
  [0:a]asplit=2[q0][q1];
  [q0]atrim=0:${D0},asetpts=PTS-STARTPTS[r0];
  [q1]atrim=${D1},asetpts=PTS-STARTPTS[r1];
  [r0][r1]acrossfade=d=${JOINX}:c1=tri:c2=tri,
       apad=whole_dur=${TOTAL},afade=t=out:st=${ASTART}:d=${AFADE}[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -profile:v high -level 4.2 -preset slow \
  -crf "${CRF:-19}" -maxrate 16M -bufsize 24M -pix_fmt yuv420p -r 30 \
  -x264-params keyint=60:min-keyint=30:scenecut=0 \
  -c:a aac -b:a 256k -ar 48000 \
  -t "$TOTAL" "$OUT"

echo "wrote $OUT"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
