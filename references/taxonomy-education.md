# Taxonomy — Video Edukasi (education)

20 referensi TikTok di `catalog.json` → kategori `education`.

Ciri kategori ini: **informasi lebih penting daripada efek**. Tujuan utamanya bukan
"keren", tapi "paham dalam 20 detik tanpa suara". Karena itu aturan smooth-nya berbeda:
animasi harus *menghilangkan diri* setelah selesai.

---

## Struktur makro: 4-bagian (explainer 15–40 detik)

| Bagian | Durasi | Fungsi | Visual |
| --- | --- | --- | --- |
| **Hook / pertanyaan** | 3–5 s | bikin penasaran | 1 kalimat besar, 2–3 baris |
| **Isi** | 6–15 s | 3 poin maksimum | teks + 1 ikon/garis per poin |
| **Bukti / data** | 3–6 s | angka, chart, timeline | chart tumbuh / angka naik |
| **Kesimpulan / CTA** | 3–5 s | 1 kalimat aksi | teks besar, sering pakai mask |

Aturan penting: **maksimum 3 poin**. Poin ke-4 selalu hilang dari ingatan penonton.

---

## Resep A — `explainer-bullets` (paling umum)

Implementasi lengkap: `examples/education.scene.json`.

```
0.0s  bg + accent bar wipe (20f) + kicker "EDUKASI ..." slideRight 18f
0.9s  pertanyaan 2 baris, stagger per kata 4f, slideUp 20f
3.3s  poin 1 slideRight 18f (jarak 56)
4.7s  poin 2  → +40f  (interval antar poin ≈ 1.3 s = 40f)
6.0s  poin 3
8.7s  chart fade 18f, bar tumbuh stagger 5f (30f per bar)
10s   catatan kecil di bawah chart
15.9s pertanyaan out (maskDown 18f)
15.9s closing maskUp 20f
```

Interval antar poin harus **konsisten** (40f). Ritme yang tidak rata membuat penonton
merasa videonya "rusak", walaupun tiap animasi baik.

---

## Resep B — `timeline-history`

* Garis horizontal `line` dengan `clipLeft 0 → 100` selama 60f (linear — ini satu dari
  sedikit tempat `linear` dibenarkan).
* 4–6 titik: `circle` popIn stagger 10f, mengikuti posisi garis saat ini.
* Label tahun: fade 12f, di atas/bawah titik bergantian (hindari tabrakan).
* Highlight 1 titik: scale 1 → 1.3, warna aksen, lalu tetap.

---

## Resep C — `data-reveal` (chart / angka)

| Langkah | Frame | Catatan |
| --- | --- | --- |
| Axes masuk | 0–14 | `clipTop 100→0` atau fade |
| Bar tumbuh | 14–50 | stagger 4f, `scaleY 0→1`, easeOutQuint |
| Angka naik | 50–90 | counter easeOutExpo |
| Annotation | 90–110 | panah/garis + label muncul |
| Freeze | 110–170 | **diam** — ini waktunya penonton membaca |

Bar chart jangan pernah tumbuh dari atas (origin harus bottom). `transform-origin: bottom center`.

---

## Resep D — `comparison`

Dua kolom; selalu ada "kunci" visual yang sama untuk keduanya (mis. kartu dengan radius sama).

```
kolom_kiri  : x -250, slideLeft 16f
kolom_kanan : x +250, slideRight 16f  (interval 4f setelah kiri)
divider     : line vertikal, tinggi 0 → 460 (18f)
kesimpulan  : bottom, fade 14f setelah kedua kolom selesai (≥ 14f jeda)
```

Warna: kiri = muted/merah redup, kanan = aksen/hijau. Kontras warna menyampaikan kesimpulan
tanpa perlu kalimat.

---

## Resep E — `step-by-step` (tutorial)

* Nomor besar di kiri (120–180 px), teks di kanan (36–42 px).
* Tiap langkah: nomor popIn (12f) → teks slideRight 16f → **tetap diam** selama langkah aktif.
* Langkah sebelumnya meredup (opacity 1 → 0.35, 12f) tanpa menghilang — menjaga konteks.
* Checkmark muncul di langkah yang selesai: `shape` line + `clipLeft` atau SVG path.

---

## Tipografi untuk edukasi

| Elemen | Ukuran @1080×1920 | Weight |
| --- | --- | --- |
| Pertanyaan | 104–140 | 800–900 |
| Poin | 40–46 | 500–600 |
| Angka besar | 180–260 | 900 |
| Label / sumber | 24–28 | 500 |

Line-height poin 1.25–1.4 (lebih lega daripada ads, karena dibaca, bukan dipindai).
Maksimum **±38 karakter per baris** di 1080 px.

---

## Timing baca (paling penting di kategori ini)

Rumus kasar: **waktu baca (ms) ≈ jumlah karakter × 35 ms** untuk teks yang sudah muncul.
Untuk 42 karakter → ±1.5 detik *setelah* animasi selesai.

Artinya: poin dengan 40 karakter butuh 18f animasi + 45f diam = 63f sebelum poin berikutnya
boleh bergerak. Itulah sumber angka interval 40–70f pada resep di atas.

---

## Palette & type default (education)

| Token | Nilai |
| --- | --- |
| bg | `#080A12` (biru sangat gelap) |
| aksen | `#2EE6A8` (mint) atau `#4C8DFF` (biru) |
| teks | `#F5F7FA` |
| muted | `#8892A6` |
| surface | `#121624` (kartu) |

Latar gelap + satu aksen = paling aman untuk teks panjang. Hindari gradient 2 warna pada
teks edukasi (menurunkan kontras).

---

## Kesalahan paling sering di kategori education

1. Poin muncul lebih cepat daripada waktu baca → penonton tertinggal, lalu berhenti menonton.
2. Terlalu banyak efek per poin (setiap poin punya animasi berbeda = melelahkan).
3. Chart dianimasikan terus (loop) sehingga sulit dibaca.
4. Tidak ada jeda diam. Video edukasi butuh ≥ 40% durasi dalam keadaan *static*.
5. Font terlalu kecil: < 34 px di 1080×1920 tidak terbaca di ponsel.
