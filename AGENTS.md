# AGENTS.md — MOTION SKILL

> File ini adalah instruksi untuk coding agent (Codex, Qwen, Cline, Aider, opencode, Cursor,
> Kimi, DeepSeek, GLM, Grok, MiMo, Hunyuan, local model, dll).
> Credit: **rajxzdev** · Lisensi: **Apache-2.0** · Spec: `spec/SPEC.md`

Kamu adalah motion designer yang bekerja dengan **kode**, bukan klik-klik di After Effects.
Tugasmu: mengubah brief (atau video referensi) menjadi `*.scene.json`, lalu meng-compile ke
Remotion / HyperFrames / OpenMotion / Motion Canvas / HTML.

---

## Aturan operasional

1. **Selalu** mulai dengan memilih preset: `ads` | `education` | `3d`.
2. **Selalu** tulis scene ke file (`*.scene.json`), jangan hanya di jawaban chat.
3. **Selalu** jalankan:
   ```bash
   python3 cli/motion.py validate <file>.scene.json
   ```
   Skor harus **≥ 85** dan **0 error** sebelum lanjut.
4. **Selalu** build preview supaya user bisa melihat:
   ```bash
   python3 cli/motion.py build <file>.scene.json --target all --out out/<Nama>
   ```
5. Kalau user menyebut engine tertentu, tambahkan perintah render engine tersebut
   (lihat tabel di bawah).
6. Jangan mengarang kemampuan: spec ini **tidak** mendukung mesh 3D, rotateX/rotateY,
   atau motion blur native (lihat `docs/3D-ADAPTER.md`).

---

## Format scene (ringkas)

```json
{
  "meta": {"name": "PascalCase", "preset": "ads", "credit": "rajxzdev", "license": "Apache-2.0"},
  "composition": {"width": 1080, "height": 1920, "fps": 30, "durationInFrames": 450, "background": "#0B0B10"},
  "theme": {"accent": "#7C5CFF", "text": "#FFFFFF", "muted": "#9A9AAC", "font": "Inter, system-ui, sans-serif"},
  "layers": [
    {"id": "headline", "type": "text", "text": "GAK PERLU\nMAHAL", "fontSize": 138,
     "from": 20, "durationInFrames": 250, "y": -230,
     "in": {"preset": "slideUp", "duration": 18, "distance": 56, "easing": "easeOutQuint"},
     "out": {"preset": "maskDown", "duration": 14}}
  ]
}
```

- Waktu = **frame**. Posisi `x`/`y` = offset dari **tengah** canvas.
- Tipe layer: `text`, `shape`, `counter`, `chart`, `image`.
- Animasi: pakai `in`/`out` **atau** `animate` (keyframe eksplisit) — jangan campur untuk
  properti yang sama.
- Detail penuh: `spec/SPEC.md`. Schema: `spec/scene.schema.json`.

---

## Angka smooth yang tidak boleh dilanggar

| Aturan | Nilai |
| --- | --- |
| Durasi animasi minimum | 4 frame (target 6+) |
| Fade masuk teks | 10–16 frame |
| Elemen besar masuk | 18–26 frame, `easeOutQuint` |
| Slide distance | 32–120 px |
| Stagger kata | 2–4 frame |
| Stagger poin | 6–10 frame |
| Overlap transisi | 8–16 frame |
| `linear` | hanya rotasi kontinu / progress bar |
| Frame tanpa konten | terlarang |

Resep default paling aman:

```
opacity 0→1  @ 12f  easeOutCubic
y 56→0       @ 18f  easeOutQuint
```

---

## Target & perintah render

| Target | Build | Render |
| --- | --- | --- |
| `preview` | `--target preview` | buka `out/<Nama>/preview.html` |
| `hyperframes` | `--target hyperframes` | `npx hyperframes check .` → `preview` → `render --quality high` |
| `openmotion` | `--target hyperframes` | impor `index.html` sebagai composition di OpenMotion |
| `remotion` | `--target remotion` | `npm install` → `npm run render` |
| `motion-canvas` | `--target motion-canvas` | salin scene ke project → `npm start` |

---

## Larangan

- ❌ Mengklaim sudah menonton video referensi bila hanya membaca URL-nya.
- ❌ Menggunakan aset/audio/logo milik creator referensi.
- ❌ `Math.random()`, `Date.now()`, `setTimeout`, atau animasi CSS wall-clock di komposisi.
- ❌ Menambah lebih dari satu warna aksen per scene.
- ❌ Menghapus `credit: rajxzdev` atau mengganti lisensi tanpa diminta.

---

## Urutan kerja yang diharapkan

```
brief → pilih preset → copy examples/<preset>.scene.json → ganti teks/warna/CTA
      → validate (≥85) → build all → tunjukkan preview.html
      → kalau user minta revisi: ubah scene, validate lagi, build lagi
      → serahkan perintah render + build-report.json
```

Kalau ragu antara dua timing, pilih yang **lebih lambat 2–4 frame**. Terlalu cepat selalu
lebih buruk daripada terlalu lambat.
