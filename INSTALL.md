# INSTALL — pasang MOTION SKILL di agent apa pun

Skill ini **model-agnostic**. Isinya teks (markdown + JSON) + satu CLI Python (stdlib saja).
Tidak ada API key, tidak ada telemetry, tidak ada vendor lock-in.

Cara kerjanya: agent membaca `SKILL.md` sebagai instruksi, lalu memakai `cli/motion.py` untuk
memvalidasi & meng-compile scene.

---

## 0. Syarat minimum

| Untuk | Butuh |
| --- | --- |
| Membuat & validasi scene | Python **3.9+** (tanpa pip install) |
| Preview | browser apa pun (file `preview.html` mandiri) |
| Render Remotion | Node **18+**, npm |
| Render HyperFrames / OpenMotion | Node **22+**, FFmpeg, Chrome/Chromium |
| Render Motion Canvas | Node **18+** |

Cek cepat:

```bash
python3 cli/motion.py doctor
```

---

## 1. Struktur folder (setelah ekstrak zip)

```
motion-skill/
├── SKILL.md          ← entry point untuk agent
├── AGENTS.md         ← entry point untuk agent berbasis AGENTS.md
├── GEMINI.md         ← entry point khusus Gemini
├── llms.txt          ← ringkasan untuk LLM/local model
├── cli/motion.py     ← CLI
├── spec/ references/ presets/ examples/ docs/ renderers/
```

Simpan folder ini **di dalam project** (mis. `./motion-skill/`) supaya path relatif tetap valid.

---

## 2. Claude Code / Claude Desktop (Agent Skills)

Claude memakai folder skill dengan file `SKILL.md` + frontmatter YAML (sudah disiapkan).

```bash
# global (semua project)
mkdir -p ~/.claude/skills
cp -r motion-skill ~/.claude/skills/motion-skill

# atau per-project
mkdir -p .claude/skills
cp -r motion-skill .claude/skills/motion-skill
```

Lalu di Claude Code:

```
> /skills                      # pastikan "motion-skill" terdaftar
> pakai motion-skill: bikin iklan 12 detik 1080x1920 untuk kopi susu, output Remotion
```

Kalau skill tidak terdeteksi: pastikan `SKILL.md` ada di **root** folder skill dan blok
`---` frontmatter tidak rusak.

---

## 3. OpenAI Codex / agent berbasis AGENTS.md

`AGENTS.md` sudah disiapkan di root. Dua cara:

```bash
# A. taruh di root project (Codex otomatis membaca)
cp motion-skill/AGENTS.md ./AGENTS.md

# B. tunjuk manual dari AGENTS.md kamu
echo 'Baca dan patuhi ./motion-skill/AGENTS.md untuk semua tugas video/motion.' >> AGENTS.md
```

Untuk ChatGPT (web) tanpa akses file: tempel isi `AGENTS.md` + `spec/SPEC.md` sebagai
system/custom instruction, lalu paste scene JSON ke chat.

---

## 4. Gemini CLI / Gemini Code Assist

```bash
# Gemini membaca GEMINI.md di root project
cp motion-skill/GEMINI.md ./GEMINI.md
# opsional: konteks tambahan
cp motion-skill/spec/SPEC.md ./SPEC.md
```

Di Gemini CLI: `> baca GEMINI.md dan SPEC.md, lalu buat scene iklan 15 detik`

---

## 5. Cursor / Windsurf / VS Code + Copilot

```bash
mkdir -p .cursor/rules
cp motion-skill/SKILL.md .cursor/rules/motion-skill.mdc    # Cursor Project Rules
# Windsurf:
mkdir -p .windsurf/rules && cp motion-skill/SKILL.md .windsurf/rules/motion-skill.md
# Copilot:
echo '# motion-skill: lihat .cursor/rules/motion-skill.mdc' >> .github/copilot-instructions.md
```

Tambahkan juga `@motion-skill/spec/SPEC.md` di chat saat butuh detail format.

---

## 6. Qwen Code / DeepSeek / Kimi / GLM / Grok / MiMo / Hunyuan / Muse / local LLM

Semua agent ini menerima konteks berupa teks. Pilih salah satu:

```bash
# A. agent CLI yang membaca AGENTS.md (Qwen Code, opencode, cline, aider, dll)
cp motion-skill/AGENTS.md ./AGENTS.md

# B. agent yang menerima file konteks
#    tempel/unggah: motion-skill/llms.txt  (ringkasan 1 file, ~6 KB)
#    tambahan bila perlu: spec/SPEC.md, references/smooth-motion.md
```

Untuk **local model** (Ollama, LM Studio, llama.cpp) dengan konteks terbatas:

| Budget konteks | File yang dimuat |
| --- | --- |
| ≤ 8k token | `llms.txt` saja (+ 1 contoh scene) |
| 8k–32k | `llms.txt` + `spec/SPEC.md` + `presets/ads.json` |
| ≥ 32k | `SKILL.md` + `spec/SPEC.md` + `references/smooth-motion.md` + `examples/*.json` |

Model kecil tetap bisa dipakai: **biarkan dia hanya menulis scene JSON**, lalu kamu (atau
model lebih besar) menjalankan `cli/motion.py validate` — validator menangkap kesalahan
timing/easing yang biasanya dilewatkan model kecil.

---

## 7. OpenMotion / HyperFrames

Skill ini menghasilkan HTML komposisi yang siap dipakai keduanya:

```bash
python3 cli/motion.py build examples/ads.scene.json --target hyperframes --out out/ads
cd out/ads/hyperframes

# HyperFrames
npx hyperframes check .
npx hyperframes preview
npx hyperframes render --quality high -o ads.mp4

# OpenMotion: salin index.html sebagai composition baru (engine-nya HyperFrames)
# di UI OpenMotion → New composition → paste isi index.html
```

Opsional: pasang juga skill resmi HyperFrames (`npx skills add heygen-com/hyperframes`) kalau
butuh katalog 450 block bawaan mereka. Keduanya bisa hidup berdampingan.

---

## 8. Remotion

```bash
python3 cli/motion.py build examples/ads.scene.json --target remotion --out out/ads
cd out/ads/remotion
npm install
npm run dev       # Remotion Studio
npm run render    # → out/AdsFlashSale.mp4
```

> Remotion punya lisensi komersial sendiri (gratis untuk individu & tim ≤ 3 orang).
> Skill ini Apache-2.0, tapi runtime Remotion tetap tunduk pada lisensi Remotion.

---

## 9. Motion Canvas

```bash
npm init @motion-canvas@latest      # buat project baru
python3 cli/motion.py build examples/ads.scene.json --target motion-canvas --out out/ads
cp out/ads/motion-canvas/src/scenes/adsFlashSale.ts <project>/src/scenes/
npm start
```

---

## 10. Verifikasi instalasi

```bash
bash scripts/verify.sh
```

Script ini menjalankan: `doctor` → `validate` 3 contoh → `build all` ke folder sementara →
cek semua output ada. Kalau semuanya hijau, skill siap dipakai.

---

## 11. Update / hapus

```bash
# update
rm -rf ~/.claude/skills/motion-skill && cp -r motion-skill ~/.claude/skills/

# hapus (tidak ada yang tertinggal di sistem)
rm -rf ~/.claude/skills/motion-skill
```

Tidak ada dependency global yang dipasang oleh skill ini.

---

## 12. Troubleshooting cepat

| Gejala | Penyebab | Solusi |
| --- | --- | --- |
| `ModuleNotFoundError: core` | menjalankan CLI dari folder lain | jalankan dari root skill, atau `python3 /path/motion-skill/cli/motion.py` |
| Skill tidak terdeteksi Claude | `SKILL.md` tidak di root folder skill | pindahkan ke root, cek frontmatter |
| Preview kosong | scene `.scene.json` belum di-build | `python3 cli/motion.py build ... --target preview` |
| HyperFrames gagal render | Node < 22 / FFmpeg tidak ada | `npx hyperframes doctor` |
| Animasi terasa patah | durasi < 6f / easing linear | `motion.py validate -v`, lihat `references/smooth-motion.md` |
| Font berubah saat render | font tidak dimuat sebelum frame 0 | pakai `@remotion/google-fonts` atau `@font-face` lokal |

Detail: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).
