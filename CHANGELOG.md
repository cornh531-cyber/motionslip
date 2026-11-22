# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/id/1.1.0/) · SemVer.

## [1.0.0] — 2026-11-23

Rilis pertama. Credit: **rajxzdev** · Lisensi: **Apache-2.0**.

### Ditambahkan
- `spec/SPEC.md` + `spec/scene.schema.json`: satu format scene → banyak engine (v1.0.0).
- `cli/motion.py`: `validate`, `build`, `new`, `list`, `references`, `doctor`.
- Compiler 4 target: `preview.html` (dependency-free), HyperFrames/OpenMotion,
  Remotion (TSX), Motion Canvas (TS).
- Validator + smoothness lint: 20+ aturan (durasi minimum, easing, overlap, dead air,
  overflow teks, konflik keyframe) dan skor 0–100.
- 21 easing dengan implementasi identik di Python / JS / TS / GSAP / Motion Canvas.
- 11 preset masuk + 6 preset keluar, di-expand ke keyframe oleh compiler.
- 3 contoh scene siap render: `ads` (15 s), `education` (18 s), `3d` (10 s).
- Library referensi: 60 link TikTok (20 iklan, 20 edukasi, 20 3D) dengan URL kanonik
  hasil resolve + worksheet studi.
- Dokumentasi: `SKILL.md`, `INSTALL.md` (12 agent/engine), `AGENTS.md`, `GEMINI.md`,
  `llms.txt`, `references/smooth-motion.md`, 3 taxonomy resep, `docs/PROMPTS.md`,
  `docs/WORKFLOW-reference-to-motion.md`, `docs/TROUBLESHOOTING.md`, `docs/FAQ.md`,
  `docs/3D-ADAPTER.md`.
- `scripts/install.sh`, `scripts/verify.sh`.

### Catatan
- Ingest isi video referensi belum otomatis (TikTok 403 untuk request non-browser).
  Yang otomatis: resolve short link → URL kanonik + video id + creator.
