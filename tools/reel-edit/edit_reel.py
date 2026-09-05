#!/usr/bin/env python3
"""
edit_reel.py - Interview -> social reel pipeline (Hebrew / RTL aware).

Stages, runnable one at a time:

  fetch       download the source video (yt-dlp)
  transcribe  Hebrew ASR with word-level timestamps -> transcript.json / .txt
  build       cut the segments listed in cuts.json, burn symmetric subtitles,
              render the reel in the aspect ratio you ask for

The editorial decisions live in cuts.json: a list of segments lifted from the
transcript, each tagged with its speaker. This script never invents, reorders
or re-words speech - it cuts on the timecodes you give it and renders the
words already in the transcript.

  python3 edit_reel.py fetch      --url https://t.me/i24NewsIL/43876 --work work/
  python3 edit_reel.py transcribe --work work/
  #  ... review work/transcript.txt, then write work/cuts.json ...
  python3 edit_reel.py build      --work work/ --aspect 9:16
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# --------------------------------------------------------------------------
# External binaries
# --------------------------------------------------------------------------

def ffmpeg_bin() -> str:
    exe = os.environ.get("FFMPEG_BINARY") or shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg not found. Install it, or: pip install imageio-ffmpeg")


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-4000:] + "\n" + proc.stderr[-4000:] + "\n")
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd[:6])} ...")


def probe_duration(path: Path) -> float | None:
    probe = os.environ.get("FFPROBE_BINARY") or shutil.which("ffprobe")
    if not probe:
        return None
    try:
        out = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except Exception:
        return None


# --------------------------------------------------------------------------
# Fonts and text measurement
# --------------------------------------------------------------------------

# Ratio of advance width to font size, averaged over Hebrew text. Only used
# when Pillow is missing and we cannot measure the real font.
HEBREW_ADVANCE_RATIO = 0.52


@lru_cache(maxsize=8)
def resolve_font(family: str | None) -> tuple[str, str | None]:
    """Return (family name for ASS, path to a file we can measure with).

    libass resolves fonts through fontconfig, so the name is what matters for
    rendering; the file is only needed so Pillow can measure the same glyphs.
    """
    def fc(*args: str) -> str | None:
        try:
            out = subprocess.run(["fc-match", *args], capture_output=True,
                                 text=True, check=True).stdout.strip()
            return out or None
        except Exception:
            return None

    query = family or ":lang=he"
    name = fc("-f", "%{family}", query) or family or "DejaVu Sans"
    name = name.split(",")[0]
    path = fc("-f", "%{file}", query)
    return name, path


class Measurer:
    """Measures rendered text width in ASS script pixels."""

    def __init__(self, font_path: str | None, size: int):
        self.size = size
        self._font = None
        if font_path:
            try:
                from PIL import ImageFont
                self._font = ImageFont.truetype(font_path, size)
            except Exception:
                self._font = None

    def width(self, text: str) -> float:
        if self._font is not None:
            return self._font.getlength(text)
        return len(text) * self.size * HEBREW_ADVANCE_RATIO

    @property
    def exact(self) -> bool:
        return self._font is not None


# --------------------------------------------------------------------------
# Symmetric line breaking
# --------------------------------------------------------------------------

def balance_lines(text: str, m: Measurer, max_width: float,
                  max_lines: int = 2) -> list[str]:
    """Break `text` into at most `max_lines` visually symmetric lines.

    Symmetric means: among every way of breaking on word boundaries into the
    fewest lines that still fit `max_width`, take the one whose lines are
    closest to equal *rendered* width. Balancing on character counts instead
    drifts badly in a proportional font - the widest Hebrew letters are close
    to twice the narrowest - and a stack of subtitles that is symmetric by
    character count still reads as ragged on screen.
    """
    words = text.split()
    if not words:
        return []
    for n in range(1, max_lines + 1):
        best = _split_into(words, n, m, max_width)
        if best is not None:
            return best
    # Unreachable via chunk_text, which only emits chunks that fit. Reached by
    # a direct caller, or by a single word wider than max_width. Wrap greedily
    # and let the block run tall: an extra line costs less than text clipped at
    # the frame edge.
    return _greedy(words, m, max_width)


def _greedy(words: list[str], m: Measurer, max_width: float) -> list[str]:
    lines, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if cur and m.width(cand) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def _split_into(words: list[str], n: int, m: Measurer,
                max_width: float) -> list[str] | None:
    """The most symmetric split of `words` into exactly `n` lines, or None."""
    if n == 1:
        line = " ".join(words)
        return [line] if m.width(line) <= max_width else None

    best: tuple[float, list[str]] | None = None

    def recurse(start: int, remaining: int, acc: list[str]) -> None:
        nonlocal best
        if remaining == 1:
            line = " ".join(words[start:])
            if not line or m.width(line) > max_width:
                return
            lines = acc + [line]
            widths = [m.width(x) for x in lines]
            cost = max(widths) - min(widths)
            if best is None or cost < best[0]:
                best = (cost, lines)
            return
        for end in range(start + 1, len(words) - remaining + 2):
            line = " ".join(words[start:end])
            if m.width(line) > max_width:
                break
            recurse(end, remaining - 1, acc + [line])

    recurse(0, n, [])
    return best[1] if best else None


def chunk_text(text: str, m: Measurer, max_width: float,
               max_lines: int) -> list[str]:
    """Split text into cue-sized chunks, preferring clause breaks.

    A chunk grows only while `balance_lines` can still lay it out inside
    `max_lines`. Sizing chunks by a character budget overshoots: text that is
    nominally two lines long fits two lines only when a word boundary falls
    near the middle, and when none does the cue spills onto an extra line.
    """
    text = " ".join(text.split())
    if not text:
        return []

    def fits(ws: list[str]) -> bool:
        return any(_split_into(ws, n, m, max_width) is not None
                   for n in range(1, max_lines + 1))

    out: list[str] = []
    for part in re.split(r"(?<=[.!?:;])\s+", text):
        words = part.split()
        if not words:
            continue
        if fits(words):
            out.append(" ".join(words))
            continue
        cur: list[str] = []
        for w in words:
            if cur and not fits(cur + [w]):
                out.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            out.append(" ".join(cur))
    return [c for c in out if c]


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

@dataclass
class Cue:
    start: float
    end: float
    text: str
    role: str = "a"


@dataclass
class Segment:
    start: float
    end: float
    role: str = "a"
    text: str = ""
    words: list[dict] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    return (f"{int(seconds // 3600)}:{int(seconds % 3600 // 60):02d}:"
            f"{seconds % 60:05.2f}")


def cues_for_segment(seg: Segment, m: Measurer, max_width: float,
                     max_lines: int, max_secs: float) -> list[Cue]:
    """Turn one segment into timed cues.

    With word timestamps every cue boundary lands on a real word start, so the
    subtitle neither leads nor lags the speech. Without them the text is spread
    across the segment in proportion to its length, close enough over a cut of
    a few seconds.
    """
    chunks = chunk_text(seg.text, m, max_width, max_lines)
    if not chunks:
        return []

    words = [w for w in seg.words if w.get("word", "").strip()]
    if words:
        cues, wi = [], 0
        for chunk in chunks:
            take = words[wi:wi + len(chunk.split())]
            if not take:
                break
            start = float(take[0].get("start", seg.start))
            end = float(take[-1].get("end", seg.end))
            if max_secs and end - start > max_secs:
                end = start + max_secs
            cues.append(Cue(max(seg.start, start),
                            min(seg.end, max(end, start + 0.4)),
                            chunk, seg.role))
            wi += len(take)
        if cues:
            return cues

    cues, t = [], seg.start
    total = sum(len(c) for c in chunks) or 1
    for chunk in chunks:
        span = seg.duration * (len(chunk) / total)
        cues.append(Cue(t, min(seg.end, t + span), chunk, seg.role))
        t += span
    return cues


# --------------------------------------------------------------------------
# Subtitle styling and output
# --------------------------------------------------------------------------

# `q` = interviewer's question, `a` = interviewee's answer. Sizes are given at
# 1080p and scaled to the output height. Keeping the two voices visually
# distinct is also what stops a pulled quote from reading as if it stood alone.
STYLES = {
    "q": dict(size=46, primary="&H00E8DCC8", outline="&H00301808",
              back="&HB4100800", bold=0, italic=-1),
    "a": dict(size=56, primary="&H00FFFFFF", outline="&H00000000",
              back="&HB4000000", bold=-1, italic=0),
}

ASPECTS = {"16:9": (1920, 1080), "9:16": (1080, 1920),
           "1:1": (1080, 1080), "4:5": (1080, 1350)}


def build_measurers(font_path: str | None, height: int,
                    font_scale: float) -> dict[str, Measurer]:
    scale = (height / 1080.0) * font_scale
    return {role: Measurer(font_path, max(12, int(st["size"] * scale)))
            for role, st in STYLES.items()}


def write_ass(cues: list[Cue], path: Path, width: int, height: int,
              font_name: str, measurers: dict[str, Measurer],
              max_width: float, max_lines: int, margin_v: int,
              boxed: bool) -> None:
    """Write the ASS subtitle file.

    Text goes out in LOGICAL order. libass here is linked against fribidi and
    applies the bidi algorithm itself, so pre-reversing the Hebrew renders it
    backwards - confirmed by rendering a frame each way.
    """
    scale = height / 1080.0
    margin_h = int((width - max_width) / 2)
    border_style = 3 if boxed else 1
    outline = max(2, int((5 if boxed else 4) * scale))
    shadow = 0 if boxed else max(1, int(2 * scale))

    out = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "WrapStyle: 2",                 # every break is ours, none are libass's
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
    ]
    for role, st in STYLES.items():
        out.append(
            f"Style: {role},{font_name},{measurers[role].size},"
            f"{st['primary']},&H000000FF,{st['outline']},{st['back']},"
            f"{st['bold']},{st['italic']},0,0,100,100,0,0,"
            f"{border_style},{outline},{shadow},"
            f"2,{margin_h},{margin_h},{int(margin_v * scale)},1"
        )

    out += ["", "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
            "MarginV, Effect, Text"]
    for cue in cues:
        role = cue.role if cue.role in STYLES else "a"
        lines = balance_lines(cue.text, measurers[role], max_width, max_lines)
        body = "\\N".join(lines).replace("\n", " ")
        out.append(f"Dialogue: 0,{ts(cue.start)},{ts(cue.end)},{role},,0,0,0,,{body}")

    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_srt(cues: list[Cue], path: Path, measurers: dict[str, Measurer],
              max_width: float, max_lines: int) -> None:
    """Companion .srt, for platforms that take an uploaded caption file."""
    def srt_ts(x: float) -> str:
        return (f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:"
                f"{int(x % 60):02d},{int(round((x - int(x)) * 1000)):03d}")

    out = []
    for i, cue in enumerate(cues, 1):
        m = measurers[cue.role if cue.role in measurers else "a"]
        body = "\n".join(balance_lines(cue.text, m, max_width, max_lines))
        out.append(f"{i}\n{srt_ts(cue.start)} --> {srt_ts(cue.end)}\n{body}\n")
    path.write_text("\n".join(out), encoding="utf-8")


# --------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------

def stage_fetch(args) -> None:
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    target = work / "source.mp4"
    if shutil.which("yt-dlp") is None:
        sys.exit("yt-dlp not found: pip install yt-dlp")
    print(f"[fetch] {args.url}")
    run(["yt-dlp", "--no-playlist", "-f", "bv*+ba/b",
         "--merge-output-format", "mp4", "-o", str(target), args.url])
    print(f"[fetch] {target} ({target.stat().st_size / 1e6:.1f} MB)")


def stage_transcribe(args) -> None:
    work = Path(args.work)
    src = work / "source.mp4"
    if not src.exists():
        sys.exit(f"missing {src} - run `fetch` first, or drop the file there.")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("pip install faster-whisper  (downloading the model needs network)")

    print(f"[transcribe] loading {args.model} ...")
    model = WhisperModel(args.model, device="auto", compute_type="auto")
    segments, _ = model.transcribe(str(src), language="he", word_timestamps=True,
                                   vad_filter=True, beam_size=5)
    data = []
    for s in segments:
        data.append({
            "start": round(s.start, 3), "end": round(s.end, 3),
            "text": s.text.strip(),
            "words": [{"word": w.word, "start": round(w.start, 3),
                       "end": round(w.end, 3)} for w in (s.words or [])],
        })
        print(f"  [{ts(s.start)} -> {ts(s.end)}] {s.text.strip()[:70]}")

    (work / "transcript.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (work / "transcript.txt").write_text(
        "\n".join(f"[{ts(d['start'])} --> {ts(d['end'])}]  {d['text']}"
                  for d in data) + "\n", encoding="utf-8")
    print(f"\n[transcribe] {len(data)} segments -> {work / 'transcript.txt'}")
    print("[transcribe] Review it, tag the speakers, write cuts.json "
          "(see cuts.example.json).")


def load_segments(work: Path) -> list[Segment]:
    cuts_path = work / "cuts.json"
    if not cuts_path.exists():
        sys.exit(f"missing {cuts_path} - see cuts.example.json for the format.")
    raw = json.loads(cuts_path.read_text(encoding="utf-8"))
    cuts = raw["cuts"] if isinstance(raw, dict) else raw

    words: list[dict] = []
    tj = work / "transcript.json"
    if tj.exists():
        for s in json.loads(tj.read_text(encoding="utf-8")):
            words.extend(s.get("words") or [])

    segs = []
    for c in cuts:
        seg = Segment(start=float(c["start"]), end=float(c["end"]),
                      role=c.get("role", c.get("speaker", "a")),
                      text=(c.get("text") or "").strip())
        if seg.duration <= 0:
            sys.exit(f"cut with non-positive duration: {c}")
        seg.words = [w for w in words
                     if seg.start - 0.05 <= w["start"] < seg.end + 0.05]
        if not seg.text and seg.words:
            seg.text = " ".join(w["word"].strip() for w in seg.words).strip()
        if not seg.text:
            sys.exit(f"cut has no text and no transcript to draw it from: {c}")
        segs.append(seg)
    return segs


def reframe_filter(width: int, height: int, fit: str) -> str:
    """Fit the source into the target frame.

    `blur` keeps the whole frame and fills the bars with a blurred copy - the
    safe default for a talking head that a hard crop would decapitate.
    `crop` centre-crops to fill.
    """
    if fit == "crop":
        return (f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1")
    return (f"split[bg][fg];"
            f"[bg]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},gblur=sigma=28,eq=brightness=-0.09[bgb];"
            f"[fg]scale={width}:{height}:force_original_aspect_ratio=decrease[fgs];"
            f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1")


def ass_path_for_filter(path: Path) -> str:
    p = str(path.resolve()).replace("\\", "/")
    return p.replace(":", r"\:").replace("'", r"\'")


def stage_build(args) -> None:
    work = Path(args.work)
    src = work / "source.mp4"
    if not src.exists():
        sys.exit(f"missing {src}")

    ff = ffmpeg_bin()
    segs = load_segments(work)
    width, height = ASPECTS[args.aspect]
    font_name, font_path = resolve_font(args.font)
    measurers = build_measurers(font_path, height, args.font_scale)
    max_width = width * args.text_width

    if not measurers["a"].exact:
        print("[build] Pillow not installed - estimating text width. "
              "`pip install pillow` for exact line balancing.")
    print(f"[build] font: {font_name}"
          f"{'' if font_path is None else ' (' + font_path + ')'}")

    parts_dir = work / "parts"
    if parts_dir.exists():
        shutil.rmtree(parts_dir)
    parts_dir.mkdir(parents=True)

    # 1. Cut each segment. Re-encoding makes the cuts frame accurate and gives
    #    every part identical encode parameters, which concat requires.
    print(f"[build] cutting {len(segs)} segments -> {args.aspect}")
    vf = reframe_filter(width, height, args.fit)
    parts = []
    for i, seg in enumerate(segs):
        out = parts_dir / f"part_{i:03d}.mp4"
        run([ff, "-y", "-loglevel", "error",
             "-ss", f"{seg.start:.3f}", "-to", f"{seg.end:.3f}", "-i", str(src),
             "-vf", vf,
             "-af", "aresample=async=1:first_pts=0,"
                    "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-r", str(args.fps), "-pix_fmt", "yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-video_track_timescale", "90000", str(out)])
        parts.append(out)
        print(f"  part {i:02d} [{seg.role}] {seg.duration:5.2f}s  {seg.text[:52]}")

    # 2. Concatenate.
    listing = parts_dir / "concat.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts),
                       encoding="utf-8")
    joined = work / "joined.mp4"
    run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", str(joined)])

    # 3. Re-time the cues onto the joined timeline.
    cues: list[Cue] = []
    offset = 0.0
    for seg in segs:
        local = Segment(0.0, seg.duration, seg.role, seg.text)
        local.words = [{"word": w["word"], "start": w["start"] - seg.start,
                        "end": w["end"] - seg.start} for w in seg.words]
        m = measurers[seg.role if seg.role in measurers else "a"]
        for cue in cues_for_segment(local, m, max_width, args.max_lines,
                                    args.max_cue_secs):
            cues.append(Cue(cue.start + offset, cue.end + offset,
                            cue.text, cue.role))
        offset += seg.duration

    ass = work / "subtitles.ass"
    write_ass(cues, ass, width, height, font_name, measurers, max_width,
              args.max_lines, args.margin_v, args.box)
    write_srt(cues, work / "subtitles.srt", measurers, max_width, args.max_lines)
    print(f"[build] {len(cues)} cues -> subtitles.ass, subtitles.srt")

    # 4. Burn in.
    final = work / f"reel_{args.aspect.replace(':', 'x')}.mp4"
    run([ff, "-y", "-loglevel", "error", "-i", str(joined),
         "-vf", f"ass={ass_path_for_filter(ass)}",
         "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf),
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "copy", str(final)])

    dur = probe_duration(final)
    print(f"\n[build] done -> {final}  ({final.stat().st_size / 1e6:.1f} MB"
          + (f", {dur:.1f}s" if dur else "") + ")")


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="download the source video")
    f.add_argument("--url", required=True)
    f.add_argument("--work", default="work")
    f.set_defaults(func=stage_fetch)

    t = sub.add_parser("transcribe", help="Hebrew ASR with word timestamps")
    t.add_argument("--work", default="work")
    t.add_argument("--model", default="large-v3")
    t.set_defaults(func=stage_transcribe)

    b = sub.add_parser("build", help="cut, subtitle and render the reel")
    b.add_argument("--work", default="work")
    b.add_argument("--aspect", default="9:16", choices=sorted(ASPECTS))
    b.add_argument("--fit", default="blur", choices=["blur", "crop"])
    b.add_argument("--font", default=None,
                   help="subtitle font family (default: fontconfig's Hebrew pick)")
    b.add_argument("--font-scale", type=float, default=1.0)
    b.add_argument("--text-width", type=float, default=0.84,
                   help="max line width as a fraction of frame width")
    b.add_argument("--max-lines", type=int, default=2)
    b.add_argument("--max-cue-secs", type=float, default=4.5)
    b.add_argument("--margin-v", type=int, default=210,
                   help="bottom margin at 1080p, scaled to the output height")
    b.add_argument("--box", action="store_true",
                   help="draw an opaque box behind each line instead of an outline")
    b.add_argument("--fps", type=int, default=30)
    b.add_argument("--crf", type=int, default=19)
    b.set_defaults(func=stage_build)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
