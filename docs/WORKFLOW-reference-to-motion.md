# Workflow — dari video referensi ke scene yang bisa dirender

Dokumen ini dipakai untuk 60 referensi di `references/catalog.json` **dan** untuk video apa pun
yang dikirim user.

> **Jujur di awal:** link TikTok tidak bisa dibaca dari environment tanpa browser (TikTok
> mengembalikan HTTP 403 untuk request non-browser). Yang sudah otomatis: short link →
> URL kanonik + `video_id` + creator. Isi video (timing, easing, teknik) **belum** di-ingest.
> Karena itu langkah 1–3 di bawah butuh manusia atau agen yang bisa melihat video.

---

## Langkah 0 — pilih referensi

```bash
python3 cli/motion.py references --category ads
```

Ambil `url` kanonik dari `catalog.json`. Buat folder kerja:

```bash
mkdir -p refs/ads-03 && cd refs/ads-03
```

---

## Langkah 1 — ekstrak bukti (bukan opini)

```bash
# video (pakai yt-dlp; hormati ToS & hak cipta — hanya untuk analisis pribadi)
yt-dlp -o ref.mp4 "<url>"

# metadata
ffprobe -v error -show_entries format=duration -of csv=p=0 ref.mp4

# frame tiap 1/10 detik untuk analisis cepat
ffmpeg -i ref.mp4 -vf fps=10 frames/f%04d.png

# contact sheet (1 gambar = 1 detik) untuk melihat struktur makro
ffmpeg -i ref.mp4 -vf "fps=1,scale=270:-1,tile=5x4" sheet.png
```

Buka `sheet.png`. Kamu sedang mencari **beat**: kapan ada perubahan besar.

---

## Langkah 2 — isi worksheet

Salin template ini ke `refs/ads-03/worksheet.md`:

```markdown
# Worksheet — ads-03 (@__mcvisuals__)

- durasi total: __ s  (__ frame @30fps)
- rasio: 1080×1920 / 1920×1080 / lain

## Beat
| # | mulai (s) | mulai (f) | isi | elemen |
|---|-----------|-----------|-----|--------|
| 1 | 0.0 | 0 | hook | teks 2 baris + glow |
| 2 | | | | |

## Elemen dominan per beat
- beat 1: ...
- beat 2: ...

## Motion yang terlihat
| elemen | properti | masuk (s/f) | easing (perkiraan) | keluar |
| teks headline | opacity+y | 0.7s / 21f | easeOutQuint | mask 0.4s |

## Teknik khusus
- mask reveal? pop? counter? chart? parallax?

## Yang akan dipakai / dibuang
- dipakai: ...
- dibuang: ... (mis. musik, footage milik creator)
```

Cara memperkirakan easing dari frame: ambil 5 frame pertama gerakan. Kalau **cepat di awal lalu
melambat** → `easeOut*`. Kalau ada **overshoot** → `back`/spring. Kalau **konstan** → `linear`.

---

## Langkah 3 — tuang ke scene

Mulai dari template terdekat:

```bash
cd ../..
python3 cli/motion.py new ads --name AdsRef03 --out scenes/ads-ref-03.scene.json
```

Ganti teks/warna/aset **milikmu sendiri** (jangan copy aset creator). Susun layer mengikuti
worksheet. Konversi detik → frame: `frame = detik × fps`.

Contoh: headline masuk 0.7 s @30fps → `"from": 21`.

---

## Langkah 4 — validasi & bandingkan

```bash
python3 cli/motion.py validate scenes/ads-ref-03.scene.json
python3 cli/motion.py build scenes/ads-ref-03.scene.json --target preview --out out/ref03
```

Buka `out/ref03/preview.html`, lalu bandingkan dengan referensi:
- scrub ke frame yang sama di keduanya (10 fps → frame 30 = 1 s),
- cek apakah **urutan kemunculan** sama,
- cek apakah **ritme** (interval antar beat) sama,
- perbedaan teks/aset itu wajar; perbedaan *timing* yang harus diperbaiki.

---

## Langkah 5 — simpan hasil bacaan ke katalog

Setelah worksheet selesai, isi `references/catalog.json`:

```json
{
  "id": "ads-03",
  "duration_s": 14.2,
  "observed": {
    "status": "ingested",
    "beats": [{"start": 0, "frames": 42, "kind": "hook"}],
    "motion": [{"element": "headline", "prop": "y", "in": 21, "dur": 18, "ease": "easeOutQuint"}],
    "techniques": ["mask-reveal", "counter"],
    "confidence": "high"
  },
  "suggested_recipe": {"id": "hook-stat-cta", "confidence": "high"}
}
```

Ini penting: **katalog yang terisi membuat skill makin pintar** untuk semua orang,
dan membuat `confidence` di masa depan jujur (bukan "inferred").

---

## Kalau tidak ada akses video / tidak boleh unduh

Alternatif yang tetap valid:

1. Minta user mengirim **3–6 screenshot** (hook, tengah, CTA). Itu cukup untuk membaca
   layout & hierarki, walau timing hanya bisa diperkirakan.
2. Gunakan **deskripsi user** + `references/taxonomy-*.md` sebagai sumber resep.
3. Tandai scene dengan `meta.notes: "timing diestimasi dari deskripsi, belum diverifikasi"`.

---

## Etika & hukum (singkat)

- Analisis struktur = boleh. **Menyalin footage/musik/logo/teks** = tidak.
- Jangan re-upload video creator dengan watermark dihapus.
- Kalau membuat "versi" dari referensi, ganti minimal: teks, warna, aset, dan (idealnya) ritme.
