#!/usr/bin/env bash
# MOTION SKILL — installer
# Credit: rajxzdev · Apache-2.0
#
# Pemakaian:
#   bash scripts/install.sh                 # interaktif
#   bash scripts/install.sh claude          # ~/.claude/skills/motion-skill
#   bash scripts/install.sh claude-project  # ./.claude/skills/motion-skill
#   bash scripts/install.sh codex           # ./AGENTS.md
#   bash scripts/install.sh gemini          # ./GEMINI.md
#   bash scripts/install.sh cursor          # ./.cursor/rules/motion-skill.mdc
#   bash scripts/install.sh path/to/folder  # salin ke folder bebas
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="motion-skill"

say()  { printf "\033[1m%s\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$*"; }

say "MOTION SKILL — installer (credit: rajxzdev · Apache-2.0)"
echo "  sumber: $ROOT"
echo

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "Pilih target:"
  echo "  1) claude          (~/.claude/skills/$NAME)"
  echo "  2) claude-project  (./.claude/skills/$NAME)"
  echo "  3) codex           (./AGENTS.md)"
  echo "  4) gemini          (./GEMINI.md)"
  echo "  5) cursor          (./.cursor/rules/$NAME.mdc)"
  echo "  6) folder lain"
  read -rp "> " CHOICE
  case "$CHOICE" in
    1) TARGET=claude ;; 2) TARGET=claude-project ;; 3) TARGET=codex ;;
    4) TARGET=gemini ;; 5) TARGET=cursor ;;
    6) read -rp "path folder: " TARGET ;;
    *) echo "batal"; exit 1 ;;
  esac
fi

install_dir() { # $1 = dest dir
  mkdir -p "$1"
  rm -rf "$1/$NAME"
  cp -r "$ROOT" "$1/$NAME"
  rm -rf "$1/$NAME/out" "$1/$NAME/__pycache__" "$1/$NAME/cli/__pycache__"
  ok "skill disalin ke $1/$NAME"
  echo "    validasi: cd $1/$NAME && python3 cli/motion.py doctor"
}

case "$TARGET" in
  claude)         install_dir "$HOME/.claude/skills" ;;
  claude-project) install_dir "$PWD/.claude/skills" ;;
  codex)
    if [ -f "$PWD/AGENTS.md" ]; then
      printf '\nBaca dan patuhi ./%s/AGENTS.md untuk semua tugas video/motion.\n' "$NAME" >> "$PWD/AGENTS.md"
      ok "AGENTS.md diperbarui (append)"
    else
      cp "$ROOT/AGENTS.md" "$PWD/AGENTS.md"; ok "AGENTS.md dibuat"
    fi
    install_dir "$PWD" ;;
  gemini)
    cp "$ROOT/GEMINI.md" "$PWD/GEMINI.md"; ok "GEMINI.md dibuat"
    install_dir "$PWD" ;;
  cursor)
    mkdir -p "$PWD/.cursor/rules"
    cp "$ROOT/SKILL.md" "$PWD/.cursor/rules/$NAME.mdc"; ok "cursor rule dibuat"
    install_dir "$PWD" ;;
  *)
    install_dir "$TARGET" ;;
esac

echo
say "Cek environment:"
if command -v python3 >/dev/null 2>&1; then
  ok "python3 $(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:3])))')"
else
  warn "python3 tidak ditemukan — CLI butuh Python 3.9+"
fi
command -v node >/dev/null 2>&1 && ok "node $(node -v)" || warn "node tidak ada (hanya perlu untuk render)"
command -v ffmpeg >/dev/null 2>&1 && ok "ffmpeg ada" || warn "ffmpeg tidak ada (dibutuhkan HyperFrames)"

echo
say "Langkah berikutnya:"
echo "  1. baca INSTALL.md bagian agent kamu"
echo "  2. contoh:"
echo "       python3 cli/motion.py list"
echo "       python3 cli/motion.py validate examples/ads.scene.json"
echo "       python3 cli/motion.py build examples/ads.scene.json --target all --out out/Ads"
echo
