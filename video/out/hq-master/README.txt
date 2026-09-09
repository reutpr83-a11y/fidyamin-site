harish-main-reel-hq.mp4  —  the full quality master

Size:    174045800 bytes
SHA-256: fde069e0b1b26d67009f87b60da44e1603a11cd1d3958bc09f8b424f8f31f148

129.8s, 1080x1920, 30fps, h264 crf 18, -13.9 LUFS, -1.3 dBTP.
Cut from two takes: the opening beat from the 4K take already in
youth-source-upload, everything after it from 06092026_155953.MOV.

Split into 2 parts so each stays under GitHub's 100 MB per file limit. The
video was NOT re-encoded: the parts are raw byte ranges of the master.

Rejoin (macOS / Linux / Git Bash), from this directory:

  cat hqmaster.*.part > harish-main-reel-hq.mp4

Rejoin (Windows PowerShell), from this directory:

  cmd /c copy /b hqmaster.00.part+hqmaster.01.part harish-main-reel-hq.mp4

Then check it prints the SHA-256 above.

You probably do not need this file. video/out/harish-main-reel-hq-1080x1920.mp4
is one file, 87 MB, and its bitrate is already higher than Instagram or
Facebook keep after they re-encode. This master is for archive and for any
future re-edit.
