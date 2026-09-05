#!/usr/bin/env python3
"""Invariants for the subtitle layout. Run: python3 test_edit_reel.py"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import edit_reel as er  # noqa: E402

POOL = ("אני חושבת שהמתנחלים בתל אביב לא צריכים להגיע לכאן בכלל ובאמת זה מה "
        "שאמרתי בראיון הזה עכשיו קיצוניים אלימות").split()


def measurers():
    _, path = er.resolve_font(None)
    return er.build_measurers(path, 1920, 1.0)


def test_no_overflow():
    """Cues never exceed max_lines, and no line exceeds max_width."""
    ms, mw = measurers(), 1080 * 0.84
    random.seed(11)
    for _ in range(2000):
        text = " ".join(random.choice(POOL) for _ in range(random.randint(1, 30)))
        for role in ("q", "a"):
            m = ms[role]
            for max_lines in (1, 2, 3):
                for chunk in er.chunk_text(text, m, mw, max_lines):
                    lines = er.balance_lines(chunk, m, mw, max_lines)
                    assert len(lines) <= max_lines, (max_lines, lines)
                    for line in lines:
                        assert m.width(line) <= mw + 0.01, (line, m.width(line))


def test_lines_are_balanced():
    """A two-line break is the most symmetric one available."""
    ms, mw = measurers(), 1080 * 0.84
    m = ms["a"]
    lines = er.balance_lines("את לא רוצה שהם יגיעו לתל אביב", m, mw, 2)
    assert len(lines) == 2
    words = "את לא רוצה שהם יגיעו לתל אביב".split()
    spread = abs(m.width(lines[0]) - m.width(lines[1]))
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if m.width(a) <= mw and m.width(b) <= mw:
            assert spread <= abs(m.width(a) - m.width(b)) + 0.01


def test_text_is_preserved():
    """Breaking into cues and lines never adds, drops or reorders a word."""
    ms, mw = measurers(), 1080 * 0.84
    m = ms["a"]
    random.seed(3)
    for _ in range(300):
        words = [random.choice(POOL) for _ in range(random.randint(1, 40))]
        text = " ".join(words)
        out = []
        for chunk in er.chunk_text(text, m, mw, 2):
            for line in er.balance_lines(chunk, m, mw, 2):
                out.extend(line.split())
        assert out == words


def test_cue_times_stay_inside_the_segment():
    seg = er.Segment(start=10.0, end=18.0, role="a",
                     text=" ".join(POOL[:14]))
    seg.words = [{"word": w, "start": 10.0 + i * 0.5, "end": 10.0 + i * 0.5 + 0.45}
                 for i, w in enumerate(POOL[:14])]
    ms = measurers()
    cues = er.cues_for_segment(seg, ms["a"], 1080 * 0.84, 2, 4.5)
    assert cues
    for cue in cues:
        assert seg.start <= cue.start < cue.end <= seg.end + 1e-6


def test_ass_is_logical_order():
    """libass applies bidi itself; pre-reversing would render Hebrew backwards."""
    ms = measurers()
    out = Path("/tmp/_test_subs.ass")
    text = "לא רוצה אותם פה"
    er.write_ass([er.Cue(0.0, 2.0, text, "a")], out, 1080, 1920,
                 "DejaVu Sans", ms, 1080 * 0.84, 2, 210, False)
    body = out.read_text(encoding="utf-8")
    assert text.split()[0] in body, "text was not written in logical order"
    assert "WrapStyle: 2" in body
    out.unlink()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(tests)} passed")
