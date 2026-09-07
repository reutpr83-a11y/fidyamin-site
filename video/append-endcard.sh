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

TOTAL=$(awk -v c="$CUT" -v k="$CARD_DUR" -v t="$TRANS" 'BEGIN{printf "%.3f", c+k-t}')
XSTART=$(awk -v c="$CUT" -v t="$TRANS" 'BEGIN{printf "%.3f", c-t}')
ASTART=$(awk -v T="$TOTAL" -v f="$AFADE" 'BEGIN{printf "%.3f", (T-f<0?0:T-f)}')
echo "cut ${CUT}s + card ${CARD_DUR}s - dissolve ${TRANS}s = ${TOTAL}s"

# The source may be shorter than the finished film once the frozen tail is
# gone, so the audio is padded with silence before the fade is applied.
ffmpeg -nostdin -y -v warning -stats -i "$IN" -i "$CARD" -filter_complex "
  [0:v]trim=0:${CUT},setpts=PTS-STARTPTS,${GRADE:+${GRADE},}format=yuv420p,fps=30[v0];
  [1:v]setpts=PTS-STARTPTS,format=yuv420p,fps=30[v1];
  [v0][v1]xfade=transition=fade:duration=${TRANS}:offset=${XSTART}[v];
  [0:a]atrim=0:${TOTAL},asetpts=PTS-STARTPTS,
       apad=whole_dur=${TOTAL},afade=t=out:st=${ASTART}:d=${AFADE}[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -profile:v high -level 4.2 -preset slow \
  -crf "${CRF:-19}" -maxrate 16M -bufsize 24M -pix_fmt yuv420p -r 30 \
  -x264-params keyint=60:min-keyint=30:scenecut=0 \
  -c:a aac -b:a 256k -ar 48000 \
  -t "$TOTAL" "$OUT"

echo "wrote $OUT"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
