#!/usr/bin/env bash
# MOTION SKILL — self-test
# Memastikan CLI, validator, dan semua compiler berjalan di mesin ini.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TMP="$(mktemp -d)"
FAIL=0

green() { printf "\033[32m%s\033[0m" "$1"; }
red()   { printf "\033[31m%s\033[0m" "$1"; }

step() { printf "\n\033[1m▸ %s\033[0m\n" "$*"; }
check() { # $1 label, $2 exit code
  if [ "$2" -eq 0 ]; then echo "  $(green ✓) $1"; else echo "  $(red ✗) $1"; FAIL=1; fi
}

step "doctor"
python3 cli/motion.py doctor >/dev/null 2>&1; check "cli/motion.py doctor" $?

step "validate 3 contoh scene (harus skor >= 85, 0 error)"
for f in ads education 3d; do
  out=$(python3 cli/motion.py validate "examples/$f.scene.json" 2>&1); rc=$?
  score=$(echo "$out" | grep -o 'score [0-9]*/100' | head -1 | grep -o '[0-9]*' | head -1)
  if [ "$rc" -eq 0 ] && [ "${score:-0}" -ge 85 ]; then
    echo "  $(green ✓) examples/$f.scene.json — skor ${score}/100"
  else
    echo "  $(red ✗) examples/$f.scene.json — rc=$rc skor ${score:-?}"; FAIL=1
    echo "$out" | sed 's/^/      /'
  fi
done

step "build semua target ke folder sementara"
for f in ads education 3d; do
  python3 cli/motion.py build "examples/$f.scene.json" --target all --out "$TMP/$f" >/dev/null 2>&1
  rc=$?
  check "build $f" $rc
done

step "cek output"
for f in ads education 3d; do
  for p in preview.html hyperframes/index.html remotion/src/Root.tsx motion-canvas/src/scenes build-report.json; do
    if [ -e "$TMP/$f/$p" ] || ls "$TMP/$f/$p"* >/dev/null 2>&1; then :; else
      echo "  $(red ✗) hilang: $f/$p"; FAIL=1
    fi
  done
  echo "  $(green ✓) artefak lengkap: $f"
done

step "kesimpulan"
if [ "$FAIL" -eq 0 ]; then
  echo "  $(green 'SEMUA HIJAU') — skill siap dipakai."
  echo "  hasil build uji: $TMP"
else
  echo "  $(red 'ADA YANG GAGAL') — lihat pesan di atas."
fi
exit "$FAIL"
