#!/usr/bin/env bash
# tjek-safezone.sh - kontaktark af en video (eller mappe med slides) med TikToks
# daekkede omraader tegnet med roedt. Brug:
#   tools/tjek-safezone.sh output/E01.mp4          -> output/E01_kontakt.jpg
#   tools/tjek-safezone.sh output/K01/             -> output/K01_kontakt.jpg
# Daekket (i 1080x1920): y<220 (soegefelt), y>1500 (navn/tekst),
#                        x>920 for y 760-1560 (like/kommentar/del).
set -euo pipefail
IN="${1:?angiv video eller mappe}"
EVERY="${2:-1}"   # et billede pr. N sekunder
BOX="drawbox=x=0:y=0:w=1080:h=220:color=red@0.45:t=fill,\
drawbox=x=0:y=1500:w=1080:h=420:color=red@0.45:t=fill,\
drawbox=x=920:y=760:w=160:h=800:color=red@0.45:t=fill,\
scale=270:480"
if [ -d "$IN" ]; then
  NAME="$(basename "${IN%/}")"; OUT="$(dirname "${IN%/}")/${NAME}_kontakt.jpg"
  N=$(ls "$IN"/*.jpg | wc -l)
  ffmpeg -y -loglevel error -framerate 1 -pattern_type glob -i "${IN%/}/*.jpg" \
    -vf "$BOX,tile=${N}x1:padding=6:color=white" -frames:v 1 "$OUT"
else
  OUT="${IN%.*}_kontakt.jpg"
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
  N=$(python3 -c "import math;print(max(1,math.ceil($DUR/$EVERY)))")
  COLS=6; ROWS=$(( (N + COLS - 1) / COLS ))
  ffmpeg -y -loglevel error -i "$IN" -vf "fps=1/$EVERY,$BOX,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{pts\:hms}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,\
tile=${COLS}x${ROWS}:padding=6:color=white" -frames:v 1 "$OUT"
fi
echo "$OUT"
