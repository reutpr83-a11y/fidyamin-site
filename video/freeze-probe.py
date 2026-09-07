#!/usr/bin/env python3
"""Finds the held tail of a clip and reports it instead of assuming it.

    python3 freeze-probe.py clip.mp4 [-35]

freezedetect thresholds are source dependent: camera footage has a noise
floor that makes moving frames obviously different, while flat motion
graphics sit still between animations and read as frozen almost throughout.
So this prints every candidate and only nominates a cut when the evidence is
unambiguous. Anything else is a question for a person, not a default.

Exit 0 with the cut on stdout when confident, exit 1 otherwise.
"""
import re, subprocess, sys

MERGE = 0.7        # events closer than this are one held frame split by noise
MIN_TAIL = 0.6     # shorter than this is a pause, not a broken ending
MAX_FRAC = 0.25    # a longer still stretch means the source is simply static
EOF_SLACK = 0.35   # how close a run must end to the file end to count


def duration(path):
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def runs(path, db):
    """Merged [start, end] stretches where the picture does not change.
    An end of None means the clip was still frozen when the file ended."""
    p = subprocess.run(
        ['ffmpeg', '-nostdin', '-v', 'info', '-i', path,
         '-vf', 'freezedetect=n=%ddB:d=0.3' % db, '-map', '0:v', '-f', 'null', '-'],
        capture_output=True, text=True)
    out, cur = [], None
    for kind, val in re.findall(r'freeze_(start|end): ([0-9.]+)', p.stderr):
        t = float(val)
        if kind == 'start':
            if cur is not None:
                if cur[1] is not None and t - cur[1] <= MERGE:
                    continue
                out.append(cur)
            cur = [t, None]
        elif cur is not None:
            cur[1] = t
    if cur is not None:
        out.append(cur)
    return out


def main():
    path = sys.argv[1]
    db = int(sys.argv[2]) if len(sys.argv) > 2 else -45
    dur = duration(path)
    rs = runs(path, db)

    print('clip %.2fs, threshold %ddB, %d still stretch(es)' % (dur, db, len(rs)),
          file=sys.stderr)
    for s, e in rs:
        print('  %7.2f to %-7s %s' % (s, '%.2f' % e if e else 'end',
                                      '<- open at the file end' if e is None else ''),
              file=sys.stderr)

    if not rs:
        print('no still stretch at this threshold. Try a looser one, for example '
              '%d, or pass CUT= by hand.' % (db + 10), file=sys.stderr)
        return 1

    start, end = rs[-1]
    open_ended = end is None
    end = dur if open_ended else end
    tail = dur - start

    if dur - end > EOF_SLACK:
        print('the last still stretch ends %.2fs before the clip does, so nothing '
              'is frozen at the end.' % (dur - end), file=sys.stderr)
        return 1
    if tail <= MIN_TAIL:
        print('the tail holds for only %.2fs, too short to be a broken ending.'
              % tail, file=sys.stderr)
        return 1
    if tail > MAX_FRAC * dur:
        print('still for %.1fs of %.1fs, %.0f%% of the clip. That is a static '
              'source, not a frozen tail. Check the frames and pass CUT= by hand.'
              % (tail, dur, 100 * tail / dur), file=sys.stderr)
        return 1
    if not open_ended:
        print('note: the run is closed rather than open at the file end',
              file=sys.stderr)

    print('%.3f' % start)
    return 0


if __name__ == '__main__':
    sys.exit(main())
