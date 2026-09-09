Original file: 06092026_155953.MOV
Size:          520673951 bytes
SHA-256:       0a9d12ff3c42f0edc1d764a145e36259491cf5f78b7d78c19c1d69d80c893861

Split into 6 byte-exact parts (95 MiB = 99614720 bytes each, last part smaller)
so every part stays under GitHub's 100 MB per-file limit. The video was NOT
re-encoded: the parts are raw byte ranges of the original file.

  155953.MOV.part00   99614720 bytes
  155953.MOV.part01   99614720 bytes
  155953.MOV.part02   99614720 bytes
  155953.MOV.part03   99614720 bytes
  155953.MOV.part04   99614720 bytes
  155953.MOV.part05   22600351 bytes

Rejoin (macOS / Linux / Git Bash), from this directory:

  cat 155953.MOV.part* > 06092026_155953.MOV

Rejoin (Windows PowerShell), from this directory:

  cmd /c copy /b 155953.MOV.part00+155953.MOV.part01+155953.MOV.part02+155953.MOV.part03+155953.MOV.part04+155953.MOV.part05 06092026_155953.MOV

Verify the rejoined file:

  sha256sum 06092026_155953.MOV     # Linux / Git Bash
  shasum -a 256 06092026_155953.MOV # macOS
  Get-FileHash 06092026_155953.MOV -Algorithm SHA256   # PowerShell

It must print: 0a9d12ff3c42f0edc1d764a145e36259491cf5f78b7d78c19c1d69d80c893861
