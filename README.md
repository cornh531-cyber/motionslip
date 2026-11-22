<div align="center">

```
  ███╗   ███╗ ██████╗ ████████╗██╗ ██████╗ ███╗   ██╗
  ████╗ ████║██╔═══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
  ██╔████╔██║██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
  ██║╚██╔╝██║██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
  ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
  ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
              S K I L L   ·   video motion as code
```

**Satu skill. Satu file scene. Empat engine. Animasi yang smooth-nya dijamin validator.**

[![license](https://img.shields.io/badge/license-Apache--2.0-7C5CFF?style=flat-square)](LICENSE)
[![credit](https://img.shields.io/badge/credit-rajxzdev-FF5C7A?style=flat-square)](https://github.com/rajxzdev)
[![python](https://img.shields.io/badge/runtime-python%203.9%2B%20%C2%B7%20zero%20deps-2EE6A8?style=flat-square)](#quickstart)
[![renderers](https://img.shields.io/badge/targets-remotion%20%C2%B7%20hyperframes%20%C2%B7%20openmotion%20%C2%B7%20motion--canvas%20%C2%B7%20html-4C8DFF?style=flat-square)](#-renderer-matrix)
[![models](https://img.shields.io/badge/works%20with-claude%20%C2%B7%20gpt%20%C2%B7%20gemini%20%C2%B7%20qwen%20%C2%B7%20deepseek%20%C2%B7%20kimi%20%C2%B7%20glm%20%C2%B7%20grok%20%C2%B7%20local-FFB43A?style=flat-square)](#-kompatibilitas-model)

</div>

---

## Apa ini?

Skill agent untuk membuat **video motion graphics lewat kode** — iklan pendek, explainer
edukasi, opener 3D/2.5D — dari satu file `*.scene.json` yang di-compile ke:

**Remotion** · **HyperFrames** · **OpenMotion** · **Motion Canvas** · **HTML preview**

Yang membuatnya beda dari kumpulan prompt: skill ini membawa **validator deterministik**
(21 easing, 20+ aturan timing, skor 0–100). Animasi tidak "smooth karena harapan", tapi karena
aturan yang ditegakkan sebelum render.

```bash
python3 cli/motion.py validate examples/ads.scene.json   # skor 100/100 ✓
python3 cli/motion.py build examples/ads.scene.json --target all --out out/Ads
open out/Ads/preview.html                                # scrub timeline, cek timing
```

---

## ⚡ Quickstart (60 detik)

```bash
unzip motion-skill.zip && cd motion-skill

python3 cli/motion.py list                              # preset, easing, target
python3 cli/motion.py validate examples/ads.scene.json   # lint + skor smooth
python3 cli/motion.py build examples/ads.scene.json --target all --out out/Ads
```

Belum mau install? Buka dulu **[`demo/ads-preview.html`](demo/ads-preview.html)** — hasil build
scene bawaan, lengkap dengan scrub bar.

Lalu buka **`out/Ads/preview.html`** → ada play/pause, scrub bar, timeline clip, dan frame
counter. Itu *frame reviewer*-mu sebelum render mahal.

Bikin scene sendiri:

```bash
python3 cli/motion.py new ads --name KopiKita --out scenes/kopi-kita.scene.json
python3 cli/motion.py validate scenes/kopi-kita.scene.json
python3 cli/motion.py build scenes/kopi-kita.scene.json --target all --out out/KopiKita
```

Butuh satu perintah untuk memastikan semuanya sehat?

```bash
bash scripts/verify.sh     # doctor + validate 3 contoh + build 4 target
```

---

## 🧠 Kenapa ada format scene sendiri?

| Kalau langsung ke engine | Kalau lewat `scene.json` |
| --- | --- |
| Timing diketik ulang per engine | Timing satu sumber, semua engine ikut |
| Tidak ada validasi | Lint 20+ aturan + skor sebelum render |
| Pindah engine = tulis ulang | `--target` ganti engine |
| Agen harus hafal 4 API | Agen cukup paham satu schema |
| Preview baru ada setelah render | `preview.html` instan, tanpa dependency |

```
        brief / 60 video referensi
                    │
                    ▼
            ┌───────────────┐
            │  scene.json   │  frame-based · deterministik · 5 tipe layer
            └───────┬───────┘
                    │
        ┌───────────▼───────────┐
        │  validate  → 0–100    │  easing · durasi · overlap · overflow · dead air
        └───────────┬───────────┘
                    │  ≥ 85
     ┌──────────────┼───────────────┬──────────────────┬───────────────┐
     ▼              ▼               ▼                  ▼               ▼
 preview.html   HyperFrames     OpenMotion         Remotion      Motion Canvas
 (browser)      (HTML+GSAP)     (engine HF)        (TSX)         (TS generator)
```

---

## 📦 Isi paket

| Path | Isi |
| --- | --- |
| `SKILL.md` | instruksi skill (frontmatter Agent Skills) — otak untuk agent |
| `AGENTS.md` `GEMINI.md` `llms.txt` | entry point untuk agent lain (Codex, Gemini, local LLM) |
| `spec/SPEC.md` + `scene.schema.json` | kontrak format scene v1.0.0 |
| `cli/motion.py` | `validate` · `build` · `new` · `list` · `references` · `doctor` |
| `references/smooth-motion.md` | **aturan emas** animasi smooth (baca ini dulu) |
| `references/taxonomy-{ads,education,3d}.md` | 14 resep siap pakai per kategori |
| `references/catalog.json` | 60 video referensi TikTok (URL ter-resolve) |
| `presets/` | token warna/type, 21 easing, 9 transisi, 3 preset gaya |
| `examples/` | 3 scene lengkap: `ads` 15s · `education` 18s · `3d` 10s |
| `renderers/` | kontrak + contoh minimal tiap engine (termasuk Lottie & CSS) |
| `demo/` | 3 preview HTML siap dibuka + 3 still PNG (bukti build) |
| `docs/` | PROMPTS · WORKFLOW · TROUBLESHOOTING · FAQ · 3D-ADAPTER |
| `scripts/` | `install.sh` (6 target) · `verify.sh` (self-test) |

---

## 🎬 Anatomi scene

```json
{
  "meta": { "name": "AdsFlashSale", "preset": "ads", "credit": "rajxzdev", "license": "Apache-2.0" },
  "composition": { "width": 1080, "height": 1920, "fps": 30, "durationInFrames": 450, "background": "#0B0B10" },
  "theme": { "accent": "#7C5CFF", "text": "#FFFFFF", "muted": "#9A9AAC" },
  "layers": [
    {
      "id": "headline", "type": "text",
      "text": "GAK PERLU\nMAHAL", "fontSize": 138, "fontWeight": 900, "uppercase": true,
      "y": -230, "from": 20, "durationInFrames": 250,
      "highlight": { "word": "MAHAL", "color": "#7C5CFF" },
      "stagger": { "mode": "word", "intervalFrames": 3,
                   "preset": { "preset": "slideUp", "duration": 18, "distance": 56, "easing": "easeOutQuint" } },
      "out": { "preset": "maskDown", "duration": 14 }
    }
  ]
}
```

Layer: `text` · `shape` · `counter` · `chart` · `image`
Animasi: 12 preset masuk · 6 preset keluar · 13 properti keyframe · 21 easing
Waktu dalam **frame**, posisi `x/y` = offset dari **tengah** canvas.

---

## ✅ Yang "smooth" itu artinya apa di sini

| Aturan | Ditegakkan |
| --- | --- |
| Animasi ≥ 4 frame (ideal ≥ 6 @30fps) | error/warning |
| `linear` hanya untuk rotasi kontinu | warning |
| Fade teks 10–16f, elemen besar 18–26f | warning |
| Slide 32–120 px | preset default |
| Stagger kata 2–4f, poin 6–10f | preset + lint |
| Keyframe tumpang tindih | warning |
| Animasi melewati akhir layer | warning |
| Ada frame tanpa konten (dead air) | warning |
| Teks overflow `maxWidth` | warning + saran `fontSize` |
| Konflik `in` preset vs keyframe eksplisit | warning |
| `Math.random` / wall-clock di komposisi | dilarang di ketiga renderer |

Bukti cepat — tiga contoh bawaan semuanya lolos:

```
ads.scene.json        10 layer · 29 animasi · 15.0s · 100/100
education.scene.json  11 layer · 28 animasi · 18.0s · 100/100
3d.scene.json          9 layer · 23 animasi · 10.0s · 100/100
```

---

## 🔌 Renderer matrix

| Target | Perintah | Output | Butuh | Kontrak kunci |
| --- | --- | --- | --- | --- |
| `preview` | `--target preview` | `preview.html` | browser | runtime mandiri, tanpa CDN |
| `hyperframes` | `--target hyperframes` | `index.html` | Node 22+, FFmpeg | clip `data-start`/`data-duration`/`data-track-index` (detik) + GSAP **paused** di `window.__timelines` |
| `openmotion` | `--target hyperframes` | composition HTML | OpenMotion | engine HyperFrames (sama) |
| `remotion` | `--target remotion` | project TSX | Node 18+ | `useCurrentFrame()` murni, `lib/easing.ts` + `lib/motion.ts` ikut digenerate |
| `motion-canvas` | `--target motion-canvas` | scene `.ts` | Node 18+ | generator + `waitFor(start)` paralel |
| `lottie` | manual | `.json` / `.lottie` | AE / dotLottie | lihat `renderers/lottie/README.md` |

Render engine:

```bash
# HyperFrames
npx hyperframes check . && npx hyperframes preview && npx hyperframes render --quality high -o ad.mp4
# Remotion
npm install && npm run render          # → out/AdsFlashSale.mp4
# Motion Canvas
npm init @motion-canvas@latest && npm start
```

---

## 🤖 Kompatibilitas model

Skill ini **tidak butuh** model tertentu — semua instruksi berbentuk markdown + JSON, dan
satu-satunya "tool" adalah CLI Python tanpa dependency.

| Model / agent | Entry point | Catatan |
| --- | --- | --- |
| Claude (Opus/Sonnet/Haiku), Claude Code | `SKILL.md` | format Agent Skills (`~/.claude/skills/`) |
| GPT / Codex / ChatGPT | `AGENTS.md` | Codex membaca otomatis dari root repo |
| Gemini / Gemini CLI | `GEMINI.md` | konteks besar → muat semua examples |
| Qwen / Qwen-Code | `AGENTS.md` | kuat untuk TSX |
| DeepSeek | `llms.txt` + `SPEC.md` | validator menahan over-engineering |
| Kimi | `AGENTS.md` | konteks panjang |
| GLM | `AGENTS.md` | bagus untuk Remotion |
| Grok | `llms.txt` | sertakan 1 contoh scene |
| MiMo / Hunyuan / Muse | `llms.txt` | kerja per-beat untuk konteks kecil |
| **Local AI** (Ollama, LM Studio, llama.cpp) | `llms.txt` | pola paling andal: salin contoh → ubah teks/warna |

Matriks lengkap + strategi budget konteks: [`config/models.json`](config/models.json).

---

## 🎯 60 referensi, jujur soal statusnya

`references/catalog.json` menyimpan **60 video TikTok** (20 iklan · 20 edukasi · 20 3D)
lengkap dengan creator, short URL, URL kanonik hasil resolve, dan `video_id`.

Status yang sebenarnya:

| Yang sudah otomatis | Yang belum |
| --- | --- |
| Resolve 60 short link → URL kanonik + video id + handle creator | Menonton/mengekstrak frame isi video (TikTok → HTTP 403 untuk request non-browser) |
| Taxonomy + 14 resep per kategori (inferensi struktural, ditandai `confidence: inferred`) | Mengisi `observed` (timing/easing per video) |

Untuk melengkapi: ikuti [`docs/WORKFLOW-reference-to-motion.md`](docs/WORKFLOW-reference-to-motion.md)
(ekstrak frame → worksheet → isi katalog → scene → bandingkan). Skill tetap 100% fungsional
hari ini karena yang dipakai adalah **grammar + validator**, bukan copy video.

> Referensi = studi struktur. Aset, musik, dan footage milik creator tidak boleh dipakai ulang.

---

## 📥 Instalasi

```bash
bash scripts/install.sh            # interaktif
bash scripts/install.sh claude     # ~/.claude/skills/motion-skill
bash scripts/install.sh cursor     # .cursor/rules/motion-skill.mdc
bash scripts/install.sh codex      # AGENTS.md di root project
```

Langkah detail per agent (Claude, Codex, Gemini CLI, Cursor, Windsurf, Copilot, Qwen, DeepSeek,
Kimi, GLM, Grok, MiMo, Hunyuan, local LLM, OpenMotion, HyperFrames, Remotion, Motion Canvas):
**[`INSTALL.md`](INSTALL.md)**.

Tanpa shell? Semua bisa manual: salin folder, tempel `llms.txt`/`SKILL.md` ke konteks, dan
pakai `examples/*.scene.json` sebagai titik awal.

---

## 🗺️ Roadmap

- [ ] Ingest penuh 60 referensi (frame extraction + `observed` terisi)
- [ ] Target tambahan: Rive, Spline scene JSON
- [ ] `motion.py render` (orchestrate ffmpeg/CLI engine dari satu perintah)
- [ ] Storyboard multi-scene (`*.story.json` → banyak scene + transisi)
- [ ] Auto-BPM: audio → beat grid → `from` tiap layer
- [ ] Web playground (scene editor + preview) di atas `preview.html`

---

## 📄 Lisensi & kredit

**Apache-2.0** — bebas dipakai komersial, wajib menyertakan [`NOTICE`](NOTICE).
Kredit utama: **rajxzdev**.

Pihak ketiga (tidak termasuk lisensi ini): video referensi TikTok (milik creator),
Remotion (Remotion License), GSAP (GreenSock License), HyperFrames/OpenMotion/Motion Canvas
(masing-masing MIT/Apache-2.0). Lihat [`NOTICE`](NOTICE) untuk detail.

<div align="center">

**Dibuat untuk agen, dipakai oleh manusia.**

`credit: rajxzdev` · `license: Apache-2.0` · `spec v1.0.0`

</div>
