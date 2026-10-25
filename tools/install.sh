#!/usr/bin/env bash
# Copies mod/ into the game's local mod folder. Re-run after every change.
# (A symlink works for the game but not the Paradox launcher, which shows it
# with no thumbnail and can't upload it.)
set -euo pipefail
src="$(cd "$(dirname "$0")/.." && pwd)/mod/"
dest="${VIC3_MOD_DIR:-$HOME/.local/share/Paradox Interactive/Victoria 3/mod}/date-stop-mod"
[ -L "$dest" ] && rm "$dest"
mkdir -p "$dest"
rsync -a --delete "$src" "$dest/"
echo "installed to $dest"
