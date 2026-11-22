# MOTION SKILL — Scene Specification v1.0

> Satu file `.scene.json` → banyak renderer (Remotion, HyperFrames/OpenMotion, Motion Canvas, HTML preview).
> Ditulis oleh **rajxzdev**. Lisensi **Apache-2.0**.

---

## 0. Kenapa ada spec ini

Setiap engine motion (Remotion, OpenMotion/HyperFrames, Motion Canvas, Lottie, Three.js) punya
model authoring yang beda:

| Engine | Model waktu | Model authoring |
| --- | --- | --- |
| Remotion | frame integer (`useCurrentFrame`) | React / TSX |
| HyperFrames & OpenMotion | detik (`data-start`, `data-duration`) | HTML + timeline seekable (GSAP) |
| Motion Canvas | detik (generator + `yield*`) | TypeScript scene |
| Lottie / Rive | persen (0–100) | JSON / proprietary |

Agen AI tidak mungkin menghafal keempatnya sekaligus. Karena itu skill ini memakai **satu format
perantara**: `*.scene.json`. Semua penalaran kreatif (timing, easing, hirarki layer) terjadi di
level scene, lalu `cli/motion.py` meng-compile ke target engine mana pun.

```
brief / reference video
        │
        ▼
  scene.json  ──► validate (smoothness lint) ──► build ──► remotion/ | hyperframes/ | motion-canvas/ | preview.html
        ▲                                                                    │
        └────────────────────── feedback loop (frame review) ◄────────────────┘
```

---

## 1. Bentuk dokumen

```jsonc
{
  "$schema": "../spec/scene.schema.json",
  "meta": {
    "name": "AdHook_FlashSale",        // PascalCase, dipakai jadi nama komponen
    "preset": "ads",                    // ads | education | 3d
    "credit": "rajxzdev",
    "license": "Apache-2.0",
    "notes": "hook 3 detik + benefit + CTA"
  },
  "composition": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "durationInFrames": 450,            // 15 s @30fps
    "background": "#0B0B10"
  },
  "theme": {
    "accent": "#7C5CFF",
    "text": "#FFFFFF",
    "muted": "#A1A1AA",
    "font": "Inter, system-ui, sans-serif",
    "radius": 28
  },
  "layers": [ /* ... */ ]
}
```

### Aturan angka

* Semua waktu di **frame** (integer), bukan detik. Konversi ke detik hanya dilakukan saat
  meng-compile ke HyperFrames/Motion Canvas (`frame / fps`).
* `fps` yang didukung: **24, 25, 30, 50, 60**. Default 30.
* Posisi `x`/`y` adalah **offset piksel dari titik tengah canvas** (0,0 = tengah).
  `x = -540` berarti mentok kiri pada canvas 1080 lebar.
* `anchor` opsional: `center` (default), `top-left`, `bottom`, `left`, `right`.

---

## 2. Layer

Semua layer berbagi field ini:

| Field | Tipe | Wajib | Keterangan |
| --- | --- | --- | --- |
| `id` | string | ✅ | unik, `snake_case` / `kebab` |
| `type` | enum | ✅ | `text` `shape` `counter` `image` `chart` |
| `from` | int (frame) | ✅ | frame global mulai tampil |
| `durationInFrames` | int | ✅ | panjang tampil |
| `track` | int | — | `data-track-index` di HyperFrames; urutan paint di Remotion |
| `x`, `y` | number | — | offset dari tengah |
| `w`, `h` | number | — | ukuran kotak (untuk wrap, shape, image) |
| `rotate` | number (deg) | — | rotasi dasar |
| `opacity` | 0–1 | — | opacity dasar |
| `blendMode` | string | — | CSS `mix-blend-mode` |
| `animate` | array | — | keyframe eksplisit |
| `in` | object | — | preset masuk |
| `out` | object | — | preset keluar |

### 2.1 `text`

```json
{ "type": "text", "text": "GAK PERLU MAHAL", "fontSize": 96, "fontWeight": 800,
  "letterSpacing": -2, "lineHeight": 1.05, "align": "center", "color": "#FFFFFF",
  "maxWidth": 840, "uppercase": true, "highlight": { "word": "MAHAL", "color": "#7C5CFF" } }
```

* `text` mendukung baris ganda `\n`.
* `stagger` (opsional) memecah teks jadi per-kata untuk animasi kata berurutan:
  `"stagger": { "mode": "word", "intervalFrames": 3, "preset": "slideUp" }`.

### 2.2 `shape`

```json
{ "type": "shape", "shape": "rect", "w": 900, "h": 220, "fill": "#15151D",
  "stroke": "#7C5CFF", "strokeWidth": 2, "radius": 32 }
```

`shape`: `rect` `circle` `line` `triangle`. `line` butuh `w` (panjang) & `strokeWidth`.

### 2.3 `counter`

```json
{ "type": "counter", "from_value": 0, "to_value": 100, "suffix": "%",
  "prefix": "", "fontSize": 220, "fontWeight": 900, "decimals": 0, "color": "#FFFFFF" }
```

Rolling number; nilainya di-ease dengan easing animasi pertama pada layer (default `easeOutExpo`).

### 2.4 `chart`

```json
{ "type": "chart", "values": [24, 48, 96, 180], "labels": ["Q1","Q2","Q3","Q4"],
  "w": 820, "h": 480, "color": "#7C5CFF", "grow": { "start": 6, "durationFrames": 30 } }
```

Bar tumbuh berurutan (stagger 4 frame) — dipakai untuk video edukasi/data.

### 2.5 `image`

```json
{ "type": "image", "src": "assets/logo.png", "w": 320, "h": 320, "fit": "contain" }
```

Untuk target HyperFrames path relatif dipakai apa adanya (`staticFile` di Remotion).

---

## 3. Animasi

### 3.1 Keyframe eksplisit

```json
"animate": [
  { "property": "opacity",   "from": 0,    "to": 1,    "start": 0,  "duration": 12, "easing": "easeOutCubic" },
  { "property": "y",         "from": 60,   "to": 0,    "start": 0,  "duration": 18, "easing": "easeOutQuint" },
  { "property": "scale",     "from": 0.92, "to": 1,    "start": 0,  "duration": 20, "easing": "springSnappy" },
  { "property": "rotate",    "from": -6,   "to": 0,    "start": 0,  "duration": 20, "easing": "easeOutBack" }
]
```

* `start` relatif terhadap `layer.from`.
* Nilai `from`/`to` untuk `x`, `y`, `rotate` adalah **absolut** (menggantikan posisi dasar layer).
  Sebaliknya, preset `in`/`out` diperlakukan sebagai **offset** dari `module x/y/rotate`:
  compiler melipat posisi dasar ke dalam keyframe preset, jadi `slideUp` pada layer `y: 250`
  menghasilkan `306 → 250`, bukan `56 → 0`.
* `opacity` selalu absolut (tidak dikalikan dengan field `opacity`).
* Properti yang didukung: `opacity` `x` `y` `scale` `scaleX` `scaleY` `rotate` `blur` `letterSpacing`
  `clipTop` `clipRight` `clipBottom` `clipLeft` (persen 0–100, dipetakan ke `inset()`).
* Satu properti boleh punya beberapa keyframe (diurutkan berdasarkan `start`).
* Sudah punya keyframe untuk sebuah properti + menulis `in`/`out` lagi → **konflik**, validator protes.

### 3.2 Preset masuk / keluar

```json
"in":  { "preset": "slideUp", "duration": 16, "distance": 56, "delay": 0, "easing": "easeOutQuint" },
"out": { "preset": "fade",    "duration": 10, "delay": 0 }
```

Preset `in`: `fade` `slideUp` `slideDown` `slideLeft` `slideRight` `scaleIn` `popIn` `blurIn`
`maskUp` `wipeRight` `typeOn` (text) `popStagger` (text+counter).

Preset `out`: `fade` `slideDown` `slideUpOut` `scaleOut` `blurOut` `maskDown`.

Preset di-expand ke keyframe oleh compiler — jadi semua renderer melihat data yang sama.

---

## 4. Kontrak determinisme (WAJIB)

Semua target renderer harus **seekable & deterministik**:

1. Tidak ada `Date.now()`, `Math.random()` tanpa seed, `setTimeout`, atau animasi CSS
   yang berjalan dengan wall-clock. Semua nilai adalah fungsi murni dari `frame`.
2. Animasi harus bisa di-*seek* ke frame mana pun tanpa tergantung urutan pemutaran
   (HyperFrames: timeline **paused**, didaftarkan di `window.__timelines`).
3. Font harus di-embed/di-*preload* sebelum frame pertama, kalau tidak akan ada FOUT
   yang bikin teks loncat antar frame.
4. Tidak ada efek yang bergantung pada frame sebelumnya (particle sim, feedback blur).

Validator menandai pelanggaran (kata kunci `Math.random`, `Date.now`, `requestAnimationFrame`
di luar runtime preview).

---

## 5. Smoothness contract (ringkas)

Detail di [`references/smooth-motion.md`](../references/smooth-motion.md). Angka minimum:

| Aturan | Nilai |
| --- | --- |
| Durasi animasi minimum | 6 frame @30fps (200 ms) |
| Durasi animasi masuk yang disarankan | 12–20 frame |
| Jarak tempuh slide | 32–120 px |
| Stagger antar item | 2–5 frame (jangan > 8) |
| Overlap transisi antar scene | 8–16 frame |
| Easing untuk gerak masuk | non-linear (`easeOut*`, spring) |
| `linear` | hanya untuk rotasi kontinu / progress bar |
| Perubahan opacity > 0.5 dalam < 4 frame | ditolak (flicker) |
| Motion blur | opsional, hanya di kecepatan > 1500 px/s |

---

## 6. Compile

```bash
python3 cli/motion.py validate examples/ads-hook.scene.json
python3 cli/motion.py build examples/ads-hook.scene.json --target all --out out/
```

Output:

```
out/
├── preview.html                 # dependency-free, bisa dibuka langsung di browser
├── hyperframes/index.html       # komposisi HyperFrames (GSAP paused timeline)
├── remotion/src/scenes/AdHook.tsx
├── motion-canvas/src/scenes/adHook.ts
└── build-report.json            # timing, skor smoothness, catatan
```
