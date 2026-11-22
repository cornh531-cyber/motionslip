# PROMPTS — siap tempel, per model

Semua prompt di bawah mengasumsikan folder skill ada di `./motion-skill/` dan agent bisa
menjalankan shell. Kalau agent tidak bisa menjalankan perintah, pakai varian "tanpa shell".

---

## Universal (Claude, GPT, Gemini, Qwen, Kimi, GLM, Grok, DeepSeek, MiMo, Hunyuan, local)

```
Kamu memakai skill ./motion-skill (baca SKILL.md + spec/SPEC.md + references/smooth-motion.md).

Tugas: buat video iklan 12 detik, 1080x1920, 30fps.
- Produk: kopi susu gula aren, brand "Kopi Kita"
- Hook: angka "70%" (diskon), benefit: "1 gelas = 2 shot espresso"
- CTA: "ORDER SEKARANG"
- Warna aksen: #7C5CFF, latar gelap
- Output: scene JSON + build ke semua target

Langkah wajib:
1. tulis scenes/kopi-kita.scene.json
2. python3 motion-skill/cli/motion.py validate scenes/kopi-kita.scene.json   (harus 0 error, skor >= 85)
3. python3 motion-skill/cli/motion.py build scenes/kopi-kita.scene.json --target all --out out/KopiKita
4. laporkan: skor, path preview.html, dan perintah render Remotion & HyperFrames
```

---

## Claude Code (slash command)

```
> /skills
> pakai motion-skill: bikin explainer 18 detik kenapa harga naik,
  3 poin, ada bar chart Q1-Q4, target HyperFrames, output di out/EduHarga
```

---

## GPT / Codex

```
Baca AGENTS.md di ./motion-skill/. Ikuti aturannya persis.
Buat scene education 20 detik: topik "bunga majemuk", 3 poin, 1 counter angka,
1 chart 4 bar. Setelah itu jalankan validate dan build --target all.
```

---

## Gemini CLI

```
Baca GEMINI.md dan spec/SPEC.md. Buat scene 3d 8 detik 1920x1080:
orb + 2 ring berlawanan arah, glow rose #FF5C7A, headline "MOTION IN 3D",
counter harga "RP 1299K". Renders: HyperFrames + Remotion.
```

---

## Qwen / DeepSeek / Kimi / GLM (sering butuh few-shot)

```
Contoh scene yang benar (ikuti strukturnya, jangan ubah schema):
<paste examples/ads.scene.json>

Sekarang buat versi baru untuk brand "Kopi Kita" (12 detik). Ubah hanya:
- meta.name, teks layer, warna theme.accent, dan durasi total (450 -> 360 frame;
  sesuaikan from & durationInFrames tiap layer agar tetap di dalam 360).
Keluarkan JSON lengkap saja, tanpa penjelasan.
```

Lalu jalankan validator sendiri: model kecil biasanya lupa menyesuaikan durasi layer.

---

## Local model (Ollama / LM Studio) — per beat

```
Konteks: <paste llms.txt>

Tulis HANYA array JSON untuk 3 layer pertama dari scene iklan 12 detik 1080x1920:
1) bg rect full-bleed
2) glow circle blur 140 opacity 0.5
3) headline "GAK PERLU MAHAL" 2 baris, fontSize 138, stagger kata 3f, slideUp 18f
Output: JSON array layer saja.
```

Gabungkan hasil per beat, lalu validate. Iterasi kecil selalu lebih akurat untuk model kecil.

---

## Prompt untuk memperbaiki yang sudah ada

```
Scene ini skor validate-nya 68. Baca references/smooth-motion.md, cari semua pelanggaran,
perbaiki dengan perubahan minimal, lalu tampilkan diff + skor baru.
<path scene>
```

```
Bandingkan preview.html dengan referensi ini (screenshot terlampir).
Fokus HANYA pada timing: apakah hook selesai <= 1.5s? apakah CTA diam >= 1s sebelum pulse?
Jangan ubah teks/warna dulu.
```

---

## Prompt untuk ganti engine

```
Scene out/AdsFlashSale sudah benar. Sekarang saya butuh versi HyperFrames untuk OpenMotion:
build --target hyperframes, lalu tunjukkan struktur data-* dan di mana timeline didaftarkan
(window.__timelines). Jangan ubah timing.
```

---

## Prompt debug render

```
Render Remotion gagal: <paste error>.
Cek: node version, package.json, path staticFile, dan apakah ada Math.random/Date.now
di src/scenes. Beri satu perbaikan paling mungkin dulu, bukan daftar panjang.
```
