#!/bin/bash
# Run the HPatches eval for each MODEL on the baseline and on the branch, one process at a time.
# Usage: run_all.sh REPO WORK DEVICE MODEL...   (after setup_baseline.sh REPO WORK)
REPO=$(realpath "$1"); WORK=$(realpath "$2"); DEV=$3; shift 3
HERE=$(cd "$(dirname "$0")" && pwd); PY=$REPO/.venv/bin/python; OUT=$WORK/results; mkdir -p "$OUT"
cp "$HERE/hpatches_eval.py" "$WORK/"   # run a copy so the eval script is the same for both trees
export HF_HUB_DISABLE_PROGRESS_BARS=1 TQDM_DISABLE=1
for m in "$@"; do
  (cd /tmp && PYTHONPATH="$WORK/k082:$WORK/base" timeout 2400 "$PY" "$WORK/hpatches_eval.py" "$m" "$OUT/$m.base.json" "$DEV" \
     > "$OUT/$m.base.log" 2>&1; echo "$m base exit=$? $(tail -1 "$OUT/$m.base.log" | cut -c1-300)")
  (cd "$REPO" && timeout 2400 "$PY" "$WORK/hpatches_eval.py" "$m" "$OUT/$m.new.json" "$DEV" \
     > "$OUT/$m.new.log" 2>&1; echo "$m new exit=$? $(tail -1 "$OUT/$m.new.log" | cut -c1-300)")
done
"$PY" "$HERE/summarize.py" "$OUT"
