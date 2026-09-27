#!/usr/bin/env bash
# Build claude-intro.mp4: fonts -> music -> frames -> mux.
set -euo pipefail
cd "$(dirname "$0")"
FFMPEG="${FFMPEG:-$(command -v ffmpeg || python3 -c 'import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())')}"
BUILD="${BUILD:-build}"
mkdir -p "$BUILD"

[ -f fonts/fonts.css ] || python3 fetch_fonts.py
python3 music.py "$BUILD/music.wav"
OUT_DIR="$BUILD" FFMPEG="$FFMPEG" node render.js
"$FFMPEG" -y -loglevel error -i "$BUILD/video-only.mp4" -i "$BUILD/music.wav" \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart claude-intro.mp4
echo "done: claude-intro.mp4"
