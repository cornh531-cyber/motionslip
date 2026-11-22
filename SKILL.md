---
name: motion-skill
description: >
  Membuat video motion graphics lewat kode — iklan pendek, explainer edukasi, dan opener 3D/2.5D —
  dengan output untuk Remotion, HyperFrames/OpenMotion, Motion Canvas, dan preview HTML.
  Pakai skill ini ketika user minta "bikin video animasi", "motion graphics", "iklan TikTok/Reels",
  "explainer video", "logo sting", "kinetic typography", atau minta meniru/meremake video referensi
  (TikTok/IG/YT) menjadi animasi yang smooth dan deterministik.
license: Apache-2.0
metadata:
  author: rajxzdev
  version: 1.0.0
  spec: spec/SPEC.md
  languages: [id, en]
  renderers: [remotion, hyperframes, openmotion, motion-canvas, html, lottie]
---

# MOTION SKILL

**Video motion = kode.** Satu file `*.scene.json` → Remotion / HyperFrames / OpenMotion /
Motion Canvas / HTML. Skill ini membuat animasi yang **smooth**, **deterministik**, dan
**bisa diaudit per frame** — bukan template acak.

> Credit: **rajxzdev** · Lisensi **Apache-2.0** · Versi spec **1.0.0**

---

## 1. Kapan skill ini dipakai

Gunakan ketika brief-nya mengandung salah satu dari:

- "bikin video iklan / promosi (TikTok, Reels, Shorts)"
- "video edukasi / explainer / penjelasan produk"
- "opener 3D", "logo sting", "kinetic typography"
- "animasi ini kurang smooth, benerin"
- "tiru video ini jadi animasi" (referensi TikTok/IG/YouTube)
- "render pakai Remotion / HyperFrames / Motion Canvas / OpenMotion"

Jangan pakai untuk: editing footage panjang (butuh NLE), VFX komposit berat, atau
3D mesh nyata (lihat `docs/3D-ADAPTER.md`).

---

## 2. Loop kerja (wajib, urut)

```
1. BRIEF      → tetapkan: tujuan, durasi, rasio, gaya (ads|education|3d), CTA/teks
2. SCENE      → tulis/buat *.scene.json (atau `new` dari preset)
3. VALIDATE   → python3 cli/motion.py validate file.scene.json   ← harus ≥ 85, 0 error
4. BUILD      → python3 cli/motion.py build file.scene.json --target all --out out/
5. REVIEW     → buka out/preview.html, periksa frame kritis (hook, beat, CTA, end)
6. FIX        → ubah scene, ulangi 3–5 (maks 3 iterasi per scene)
7. RENDER     → serahkan perintah render untuk engine pilihan user
```

Aturan besi:

- **Jangan pernah** menyerahkan hasil tanpa menjalankan `validate`.
- **Jangan pernah** menulis animasi dengan durasi < 4 frame (validator menolak).
- **Jangan pernah** memakai `Math.random()`, `Date.now()`, `setTimeout`, atau animasi CSS
  berbasis wall-clock di dalam komposisi. Semua nilai = fungsi dari `frame`.
- Kalau skor < 85: perbaiki dulu, jangan tambah efek baru.

---

## 3. Pilih preset

| Preset | Rasio | Durasi | Ciri |
| --- | --- | --- | --- |
| `ads` | 1080×1920 | 9–18 s | 3 beat (hook → benefit → CTA), headline 900, 1 aksen |
| `education` | 1080×1920 | 15–40 s | maks 3 poin, 40% durasi diam, chart/angka |
| `3d` | 1920×1080 | 6–12 s | orb/ring 2.5D, glow besar, rotasi linear |

Preset menyimpan warna, tipografi, timing, dan motion default:
`presets/{ads,education,3d}.json` + `presets/tokens.json` + `presets/easings.json`.

---

## 4. Anatomi scene (ringkas)

```json
{
  "meta": { "name": "AdsFlashSale", "preset": "ads", "credit": "rajxzdev", "license": "Apache-2.0" },
  "composition": { "width": 1080, "height": 1920, "fps": 30, "durationInFrames": 450, "background": "#0B0B10" },
  "theme": { "accent": "#7C5CFF", "text": "#FFFFFF", "muted": "#9A9AAC" },
  "layers": [
    { "id": "headline", "type": "text", "text": "GAK PERLU\nMAHAL", "fontSize": 138,
      "from": 20, "durationInFrames": 250, "y": -230,
      "stagger": { "mode": "word", "intervalFrames": 3,
                   "preset": { "preset": "slideUp", "duration": 18, "distance": 56 } },
      "out": { "preset": "maskDown", "duration": 14 } }
  ]
}
```

Detail lengkap: [`spec/SPEC.md`](spec/SPEC.md) · JSON Schema: [`spec/scene.schema.json`](spec/scene.schema.json)
· contoh siap render: [`examples/`](examples).

Tipe layer: `text` · `shape` · `counter` · `chart` · `image`.
Animasi: preset (`in`/`out`) **atau** keyframe eksplisit — jangan campur untuk properti yang sama.

---

## 5. Aturan smooth (ringkas — detail di `references/smooth-motion.md`)

| Aturan | Angka |
| --- | --- |
| Durasi animasi minimum | 4f (idealnya 6f+) |
| Masuk teks | 10–16f, `easeOutCubic` |
| Masuk elemen besar | 18–26f, `easeOutQuint` |
| Jarak slide | 32–120 px |
| Stagger kata | 2–4f |
| Stagger poin | 6–10f |
| Overlap transisi | 8–16f |
| `linear` | **hanya** rotasi kontinu / progress |
| Frame kosong | terlarang (overlap layer) |
| Waktu diam setelah masuk | ≥ 20f sebelum elemen berikut bergerak |

Resep gabungan paling aman (dipakai 80% kasus):

```
opacity 0 → 1  @ 12f  easeOutCubic
y 56 → 0       @ 18f  easeOutQuint
```

Opacity selesai lebih dulu daripada gerak → terasa "muncul lalu mendarat".

---

## 6. Output per engine

| Target | Perintah | Yang dihasilkan |
| --- | --- | --- |
| `preview` | `--target preview` | `preview.html` — runtime tanpa dependency, bisa dibuka langsung / iframe |
| `hyperframes` | `--target hyperframes` | `index.html` komposisi: `data-composition-id`, clip `data-start`/`data-duration`/`data-track-index` (detik), timeline GSAP **paused** di `window.__timelines` |
| `openmotion` | pakai `--target hyperframes` | OpenMotion memakai engine HyperFrames — drop `index.html` ke project OpenMotion |
| `remotion` | `--target remotion` | project TSX: `Root.tsx` + `scenes/<Name>.tsx` + `lib/` (easing, track, counter) |
| `motion-canvas` | `--target motion-canvas` | scene TS generator (`waitFor` + tween paralel) |
| `all` | `--target all` | semuanya + `build-report.json` |

Semua target membaca timing yang **sama** — jadi hasil preview, Remotion, dan HyperFrames
konsisten.

---

## 7. Referensi video (60 link TikTok)

`references/catalog.json` berisi 60 referensi (20 iklan, 20 edukasi, 20 3D) lengkap dengan
creator + URL kanonik hasil resolve. Gunakan sebagai **pembanding rasa**, bukan target copy
1:1. Cara mengubah referensi → scene:

1. Baca `docs/WORKFLOW-reference-to-motion.md`.
2. Ekstrak frame (`ffmpeg -vf fps=30`) → catat timing masuk/keluar tiap elemen.
3. Isi `observed` di `catalog.json`.
4. Tuang ke `scene.json` (pakai resep dari `references/taxonomy-{ads,education,3d}.md`).
5. Bandingkan `preview.html` dengan referensi, frame per frame.

---

## 8. Guardrail (hal yang tidak boleh dilakukan agen)

1. ❌ Klaim sudah "menonton" video referensi kalau hanya membaca URL.
2. ❌ Render tanpa `validate` hijau.
3. ❌ Menyalin aset/karya creator lain (musik, footage, logo). Referensi = studi struktur.
4. ❌ Menjanjikan 3D mesh nyata dari spec ini.
5. ❌ Mengubah `credit`/`license` kecuali user minta eksplisit.
6. ❌ Memakai lebih dari 1 aksen warna pada satu scene.

---

## 9. Contoh prompt yang sudah terbukti

> "Bikin iklan 12 detik 1080×1920 untuk kopi susu, hook angka '70%', CTA 'Order sekarang',
> warna ungu, render ke Remotion."

> "Ubah video referensi ads-03 dari references/catalog.json jadi scene 15 detik, tapi jangan
> tiru teksnya — ganti jadi brand aku (Nama: Kopi Kita)."

> "Explainer 18 detik: kenapa aset bisa naik, 3 poin, ada bar chart, target HyperFrames."

> "Scene 3d.scene.json ini terlalu ramai. Kurangi jadi 1 elemen berputar dan pastikan skor
> validate tetap ≥ 85."

---

## 10. File penting

```
SKILL.md                     ← kamu di sini
INSTALL.md                   ← cara pasang skill di agent apa pun
spec/SPEC.md                 ← spesifikasi scene (kontrak)
references/smooth-motion.md  ← aturan animasi smooth (baca kalau ragu)
references/taxonomy-*.md     ← resep per kategori
presets/                     ← token, easing, preset gaya
cli/motion.py                ← validator + compiler
examples/                    ← 3 scene siap pakai
docs/PROMPTS.md              ← prompt siap tempel per model
```
