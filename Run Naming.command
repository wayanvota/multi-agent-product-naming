#!/bin/zsh
set -eu
SCRIPT_DIR="${0:A:h}"
cd "$SCRIPT_DIR"
PYTHON_BIN="$(command -v python3 || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  print 'Python 3 is required. Ask Codex to check the local Python installation.'
  read '?Press Return to close.'
  exit 1
fi
RUN_DIR="$SCRIPT_DIR/runs/$(date +%Y%m%d-%H%M%S)-$$"
print 'Starting the Product naming debate using your signed-in Codex account.'
print "Results: $RUN_DIR"
if "$PYTHON_BIN" naming.py run --run-dir "$RUN_DIR"; then
  open "$RUN_DIR/shortlist.md"
else
  print "The run stopped. Its records are preserved in $RUN_DIR."
  print 'Ask Codex to inspect and resume it.'
fi
read '?Press Return to close.'
