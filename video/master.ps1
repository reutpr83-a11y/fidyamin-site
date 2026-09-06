# Master and mux, PowerShell version of master.sh.
# Two pass loudness on the score, then mux with the picture.
# Target is -14 LUFS integrated and -1 dBTP, which is what Instagram
# normalises around and leaves the file untouched.
#
#   cd fidyamin-site\video
#   .\master.ps1

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$FF = if ($env:FFMPEG) { $env:FFMPEG } else { 'ffmpeg' }
$Out   = 'out'
$Score = Join-Path $Out 'score.wav'
$Pic   = Join-Path $Out 'video-only.mp4'
$Final = Join-Path $Out 'harish-budget-reels-1080x1920.mp4'

$I = -14; $TP = -1.0; $LRA = 9

foreach ($f in @($Score, $Pic)) {
  if (-not (Test-Path $f)) { throw "missing $f. run render.js frames and sound.py first" }
}

Write-Host '== pass 1, measuring'
$raw = & $FF -hide_banner -nostats -i $Score `
  -af "loudnorm=I=$I`:TP=$TP`:LRA=$LRA`:print_format=json" -f null - 2>&1 | Out-String

$json = [regex]::Match($raw, '(?s)\{.*?\}').Value
if (-not $json) { throw 'could not read the loudnorm measurement' }
$m = $json | ConvertFrom-Json
Write-Host ("   measured  I={0}  TP={1}  LRA={2}" -f $m.input_i, $m.input_tp, $m.input_lra)

Write-Host '== pass 2, applying and muxing'
$filter = "[1:a]loudnorm=I=$I`:TP=$TP`:LRA=$LRA" +
          "`:measured_I=$($m.input_i)`:measured_TP=$($m.input_tp)" +
          "`:measured_LRA=$($m.input_lra)`:measured_thresh=$($m.input_thresh)" +
          "`:offset=$($m.target_offset)`:linear=true[a]"

& $FF -hide_banner -loglevel error -y -i $Pic -i $Score `
  -filter_complex $filter `
  -map 0:v -map '[a]' -shortest `
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 `
  -movflags +faststart $Final
if ($LASTEXITCODE -ne 0) { throw 'ffmpeg mux failed' }

Write-Host '== result'
& $FF -hide_banner -i $Final 2>&1 | Select-String 'Duration|Stream #'
& $FF -hide_banner -nostats -i $Final -af ebur128=peak=true -f null - 2>&1 |
  Select-String '^\s+(I|LRA|Peak):'
Get-Item $Final | Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB,1)}}
