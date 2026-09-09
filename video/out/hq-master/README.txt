harish-main-reel-hq.mp4  —  the full quality master

Size:    203274916 bytes
SHA-256: ee4753897e6e7ff65e8b1d639bb0423a77b1d2277a2d84e0b21bc50a0baaa174

131.3s, 1080x1920, 30fps, h264 crf 18, 12.4 Mbps, -14.1 LUFS, -1.4 dBTP.
Cut from the camera original 06092026_155953.MOV (2160x3840 HEVC, 26 Mbps).

Split into 3 parts so each stays under GitHub's 100 MB per file limit. The
video was NOT re-encoded: the parts are raw byte ranges of the master.

Rejoin (macOS / Linux / Git Bash), from this directory:

  cat hqmaster.*.part > harish-main-reel-hq.mp4

Rejoin (Windows PowerShell), from this directory:

  cmd /c copy /b hqmaster.00.part+hqmaster.01.part+hqmaster.02.part harish-main-reel-hq.mp4

Then check it prints the SHA-256 above.

You probably do not need this file. video/out/harish-main-reel-hq-1080x1920.mp4
is one file, 90 MB, and its bitrate is already higher than Instagram or
Facebook keep after they re-encode. This master is for archive and for any
future re-edit.
