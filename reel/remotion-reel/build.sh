#!/usr/bin/env bash
# Pipeline completo: voz -> tiempos -> sfx/música -> render Remotion -> loudnorm.
set -euo pipefail
cd "$(dirname "$0")"
KIT=../reel-3ias
BROWSER=${BROWSER:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}
[ -f public/voz.mp3 ] && [ "${FORCE_VOICE:-0}" != 1 ] || node scripts/voice.mjs
T=$(node -p "require('./public/timing.json').total")
(cd public
 EVENTS_ONLY=1 TIMING_DIR=$PWD python3 ../$KIT/reel5.py
 python3 ../scripts/sfx2.py sfx.wav
 if [ -f musica.mp3 ]; then
   ffmpeg -y -loglevel error -i musica.mp3 -t "$T" music.wav
 else
   python3 ../$KIT/music.py "$T" music.wav
 fi)
mkdir -p out
npx remotion render Reel3IAs out/raw.mp4 --codec h264 --pixel-format yuv420p --audio-codec aac --browser-executable="$BROWSER" --log=error
ffmpeg -y -loglevel error -i out/raw.mp4 -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89" \
  -c:a aac -b:a 192k -movflags +faststart out/reel_3IAs_final.mp4
echo "LISTO: $PWD/out/reel_3IAs_final.mp4"
