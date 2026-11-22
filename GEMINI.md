# GEMINI.md — MOTION SKILL

Kamu membuat video motion graphics **sebagai kode** dengan skill ini.

Credit: **rajxzdev** · Lisensi: **Apache-2.0** · Spec: `spec/SPEC.md` · Entry: `SKILL.md`

## Ringkas
- Input: brief (iklan / edukasi / 3D) atau video referensi dari `references/catalog.json`.
- Perantara: `*.scene.json` (frame-based, semua nilai = fungsi dari frame).
- Output: `preview.html`, HyperFrames/OpenMotion `index.html`, Remotion TSX, Motion Canvas TS.
- Tool wajib: `python3 cli/motion.py validate|build`.

## Alur
1. Pilih preset: `ads` (1080×1920, 9–18s) · `education` (1080×1920, 15–40s) · `3d` (1920×1080, 6–12s).
2. Tulis scene JSON (lihat `examples/`), mulai dari template terdekat.
3. `python3 cli/motion.py validate out.scene.json` → harus 0 error & skor ≥ 85.
4. `python3 cli/motion.py build out.scene.json --target all --out out/Nama`.
5. Laporkan skor, path preview, dan perintah render engine pilihan user.

## Angka yang wajib dipatuhi
- Animasi minimal 4 frame (target ≥ 6). Fade teks 10–16f. Elemen besar 18–26f.
- Easing masuk non-linear (`easeOutQuint` / `easeOutBack`); `linear` hanya untuk rotasi kontinu.
- Stagger kata 2–4f, poin 6–10f, overlap transisi 8–16f, tidak boleh ada frame kosong.
- Satu warna aksen per scene.

## Larangan
- Jangan klaim menonton video referensi (isi video belum di-ingest; hanya URL yang ter-resolve).
- Jangan pakai aset/audio/logo creator referensi.
- Jangan janjikan mesh 3D / rotateX / motion blur native — lihat `docs/3D-ADAPTER.md`.

## Kalau konteks terbatas
Muat `llms.txt` + `spec/SPEC.md` + satu `examples/*.scene.json`, lalu kerjakan per beat
(1 request = 1 beat) dan gabungkan.
