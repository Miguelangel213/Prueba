#!/usr/bin/env bash
# Normaliza a -14 LUFS (2 pasadas), pico real <= -2 dBFS, video yuv420p BT.709. Uso: desde remotion-reel/
set -euo pipefail
# normalización a -14 LUFS en dos pasadas (medir y aplicar) + video a yuv420p limitado BT.709
M=$(ffmpeg -hide_banner -i out/raw.mp4 -vn -af loudnorm=I=-14:TP=-2:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -loglevel error -i out/raw.mp4 \
  -vf "scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p" \
  -af "loudnorm=I=-14:TP=-2:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.79:level=disabled,aresample=48000" \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 192k -movflags +faststart out/reel_3IAs_final.mp4
