# Identifying source material

Four takes of the budget script exist, all of the same speaker in the same
terracotta shirt, and the file names do not say which is which. These tools
answer that question by measurement rather than by name.

| tool | matches on | use it when |
|---|---|---|
| `locate.py` | audio waveform | the clip has an audio track |
| `mlocate.py` | motion energy per frame | the clip is video only |
| `vlocate.py` | frame appearance | last resort, and it fails on a locked off talking head |

The reliable one for identifying **which take** a file is, is the speech mask
correlation used in `reel/main/BUILD.md`: build a binary speech mask from the
audio envelope, build the same mask from each candidate transcript's word
times, and correlate. It separates cleanly where the others do not.

Measured results, September 2026:

| file | is | peak |
|---|---|---|
| `youth-source-upload:video/src/youth-source.mp4` | first 85s of the `transcript.json` take (146.5s) | 0.455 |
| the 159s WhatsApp export | the `transcript_155953` take (156.6s) | 0.555 |
| `raw-upload:video/workA/segs/` | cut from `youth-source.mp4` | 0.96 to 0.99 on motion |
| `raw-upload:video/work/segs/` | a third setup, standing outdoors | matches nothing above |

**`youth-source.mp4` is not the take the current reel is cut from**, and the
segs add nothing that is not already in it at higher resolution.
