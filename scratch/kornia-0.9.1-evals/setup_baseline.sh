#!/bin/bash
# Baseline = upstream main + kornia 0.8.2, sharing the branch checkout's venv and submodules.
# Usage: setup_baseline.sh REPO WORK   (REPO: vismatch checkout on kornia-0.9.1 with submodules and .venv)
set -euo pipefail
REPO=$(realpath "$1"); WORK=$(realpath -m "$2"); mkdir -p "$WORK"
git -C "$REPO" fetch -q https://github.com/gmberton/vismatch main
git -C "$REPO" worktree add --detach "$WORK/base" FETCH_HEAD
rm -rf "$WORK/base/vismatch/third_party"
ln -s "$REPO/vismatch/third_party" "$WORK/base/vismatch/third_party"
uv pip install --python "$REPO/.venv/bin/python" --target "$WORK/k082" --no-deps kornia==0.8.2
cd /tmp && PYTHONPATH="$WORK/k082:$WORK/base" "$REPO/.venv/bin/python" -W ignore -c \
  "import kornia, vismatch; print('baseline:', kornia.__version__, vismatch.__file__)"
cd "$REPO" && "$REPO/.venv/bin/python" -W ignore -c \
  "import kornia, vismatch; print('new:     ', kornia.__version__, vismatch.__file__)"
