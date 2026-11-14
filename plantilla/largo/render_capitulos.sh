#!/bin/bash
export HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome
for c in "$@"; do
  cd /home/claude/largo/proj/$c
  s=$(date +%s)
  npx --yes hyperframes@0.9.41 render -o /home/claude/largo/render/$c.mp4 --crf 20 --quiet > /home/claude/largo/render_$c.log 2>&1
  echo "$c rc=$? $(( $(date +%s)-s ))s" >> /home/claude/largo/render_progress.log
done
echo FIN >> /home/claude/largo/render_progress.log
