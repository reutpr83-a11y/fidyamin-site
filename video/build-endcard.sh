#!/usr/bin/env bash
# Renders the end card to out/endcard.mp4.
#
# endcard.html and check-endcard.js are generated from video.html and
# check.js so the card can never drift from the engine that draws the
# rest of the film. They are gitignored for that reason: edit the
# originals, not the copies.
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'PY'
html = open('video.html', encoding='utf-8').read()
open('endcard.html', 'w', encoding='utf-8').write(
    html.replace('<script src="script.js">', '<script src="endcard.js">'))

chk = open('check.js', encoding='utf-8').read()
chk = chk.replace("'video.html'", "'endcard.html'")
# the 48 to 55 second window is the law for the whole film, not for one card
chk = chk.replace(
    "if (out.total < 48 || out.total > 55) fail.push('duration ' + out.total.toFixed(1) + 's outside 48 to 55');",
    "// the duration window applies to the full film, not to a single card")
open('check-endcard.js', 'w', encoding='utf-8').write(chk)
PY

export NODE_PATH="${NODE_PATH:-/opt/node22/lib/node_modules}"
echo "== QA gate"
node check-endcard.js
echo "== render"
PAGE=endcard.html NAME=endcard node render.js frames
echo "wrote out/endcard.mp4"
