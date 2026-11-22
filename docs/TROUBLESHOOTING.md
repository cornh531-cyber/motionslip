# Troubleshooting

## CLI

**`ModuleNotFoundError: No module named 'core'`**
Jalankan dari root skill: `cd motion-skill && python3 cli/motion.py ...`
atau `python3 /path/to/motion-skill/cli/motion.py ...`.

**`JSON tidak valid di ...`**
Scene JSON punya koma/tanda kutip berlebih. `python3 -m json.tool file.scene.json` untuk
melihat baris persisnya.

**Validator error "keluar canvas"**
`from + durationInFrames > composition.durationInFrames`. Perpanjang komposisi atau
pendekkan layer.

**Skor rendah padahal terlihat oke**
Lihat `-v`. Biasanya: animasi < 6f, `linear` pada gerak masuk, atau keyframe tumpang tindih.

---

## Preview

**Preview kosong / hitam**
Belum build: `--target preview`. Pastikan juga file dibuka dari disk (bukan `file://` di
dalam iframe yang memblokir JS — preview ini tidak butuh jaringan, jadi aman).

**Layer tidak muncul**
`from` terlalu besar atau `durationInFrames` terlalu kecil. Scrub timeline; cek `build-report.json`.

**Teks meluber keluar layar**
Turunkan `fontSize` atau naikkan `maxWidth`; validator sudah memberi saran angka.

**Stage kecil / terpotong**
Preview men-scale otomatis (fit). Kalau jendela sangat pendek, zoom browser ke 80%.

---

## Remotion

| Gejala | Penyebab | Solusi |
| --- | --- | --- |
| `Cannot find module 'remotion'` | belum `npm install` | `npm install` di folder project |
| Blank frame pertama | font belum dimuat | pakai `@remotion/google-fonts` atau `@font-face` + `delayRender()` |
| Render lambat | `blur` besar / banyak layer | turunkan blur, `Config.setConcurrency(4)` |
| Hasil tiap run beda | ada `Math.random`/`Date.now` | cari dengan `grep -rn "Math.random\|Date.now" src` |
| Video tidak ada audio | belum ada `<Audio>` | tambahkan layer audio terpisah |
| `staticFile` 404 | aset tidak di `public/` | pindahkan ke `public/`, referensikan tanpa `public/` |

## HyperFrames / OpenMotion

| Gejala | Solusi |
| --- | --- |
| `npx hyperframes` gagal start | butuh **Node 22+** & **FFmpeg**; jalankan `npx hyperframes doctor` |
| Render hanya 1 frame / freeze | timeline tidak `paused`, atau tidak didaftarkan di `window.__timelines` |
| Animasi "lompat" saat seek | ada animasi non-seekable (CSS transition, `setTimeout`) |
| Durasi video salah | `data-duration` root ≠ durasi timeline; root menentukan titik stop |
| Clip tidak muncul | `data-start`/`data-duration` negatif atau `data-track-index` bentrok |
| GSAP tidak ditemukan | CDN diblokir → `npm i gsap`, ganti `src` ke file lokal |

## Motion Canvas

| Gejala | Solusi |
| --- | --- |
| Type error `Txt`/`Rect` | import dari `@motion-canvas/2d` |
| Animasi bertumpuk salah | pastikan tiap tween dibungkus generator + `waitFor(start)` |
| Mask/blur tidak berefek | memang belum dipetakan (lihat `renderers/motion-canvas/README.md`) |

---

## Timing & rasa

**"Animasinya patah / kedip"** → durasi < 6 frame atau opacity berubah > 0.5 dalam < 4 frame.
**"Terlalu ramai"** → lebih dari 2 properti beranimasi bersamaan pada elemen yang sama.
**"Kosong di tengah"** → ada celah antar layer; overlap 6–10 frame.
**"Terasa lambat"** → total masuk > 30 frame untuk headline; potong, jangan tambah easing.
**"Terasa murah"** → semua easing sama dan semuanya `easeOutCubic`. Beri 1 elemen `easeOutBack`.

---

## Lisensi

- Skill ini Apache-2.0 → bebas dipakai komersial, wajib simpan `NOTICE`.
- **Remotion**: lisensi terpisah (gratis individu / tim ≤ 3; berbayar di atasnya).
- **GSAP**: cek lisensi GreenSock untuk pemakaian tertentu.
- Video referensi TikTok: milik creator; jangan didistribusikan ulang.
