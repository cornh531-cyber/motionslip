# Taxonomy — Video Iklan (ads)

20 referensi TikTok di `catalog.json` → kategori `ads`.
Library ini adalah **grammar** yang dipakai video-video iklan pendek: bukan hasil menonton
frame-per-frame tiap link (lihat `references/README.md` soal status ingest), tapi struktur
resep yang bisa langsung dipakai dan diverifikasi manual lewat worksheet di
`docs/WORKFLOW-reference-to-motion.md`.

Semua resep di bawah sudah berbentuk scene JSON — copy, ganti teks, build.

---

## Struktur makro: 3-beat (paling umum di TikTok ads)

Total 9–18 detik. Setiap beat = 1 ide, maksimum 5 detik.

| Beat | Frame (15s @30fps) | Fungsi | Elemen wajib |
| --- | --- | --- | --- |
| **Hook** | 0–135 | hentikan scroll | 1 angka besar ATAU 1 pertanyaan ATAU gerak cepat |
| **Proof / Benefit** | 135–330 | alasan percaya | 2–3 poin, atau 1 angka + label |
| **CTA** | 330–450 | perintah jelas | 1 tombol/pill + 1 kata kerja |

Aturan: beat pertama **tidak boleh** berisi nama brand. Brand masuk di beat 2–3.

---

## Resep A — `hook-stat-cta` (angka sebagai hook)

Contoh implementasi lengkap: `examples/ads.scene.json`.

```
0.0s  background + glow masuk (fade 10f, scaleIn 26f)
0.3s  eyebrow kecil ("BARU · EDISI 2026") fade 16f
0.7s  headline 2 baris, stagger per kata 3f, slideUp 18f, easeOutQuint
2.1s  subline 1 baris, slideUp 18f
3.2s  counter 0 → 70% (grow 40f, easeOutExpo) + popIn 18f
3.7s  label kecil di bawah angka
6.3s  pill CTA popIn 20f (easeOutBack) + teks CTA fade 14f
9.5s  pulse CTA (scale 1 → 1.04 → 1, 14f + 16f)
14.3s end_fade 20f
```

Kunci smooth-nya: counter **selesai** sebelum label muncul; CTA **diam 1.5s** sebelum pulse
supaya pulse terasa sebagai "ajakan", bukan bagian dari animasi masuk.

---

## Resep B — `problem-agitate-solution` (PAS)

| Segmen | Frame | Visual |
| --- | --- | --- |
| Problem | 0–120 | teks besar, warna dingin, 1 garis coret (line shape rotate -6°) |
| Agitate | 120–240 | 3 teks kecil muncul berurutan (stagger 8f), warna meredup |
| Solution | 240–360 | layer warna aksen wipe dari bawah, teks baru slideUp |
| Proof | 360–420 | badge/logo popIn + counter kecil |
| CTA | 420–480 | pill + arrow (chevron slide 6f loop) |

Warna: problem `#8A8FA6`, solution = aksen. Perubahan warna = penanda perubahan emosi.

---

## Resep C — `price-drop` (diskon / flash sale)

Elemen khas: angka coret → angka baru, dengan **count-down feel**.

```
harga_lama  : text, tampil 0f, animate: letterSpacing +, opacity 1→0.4, y -8  (12f)
strike_line : shape line, clipLeft 100→0 (14f, easeOutQuint), rotate -4
harga_baru  : counter, popIn 16f easeOutBack, grow 26f
badge       : text "-70%", rotate -8, popIn 14f + springSnappy
```

Aturan: **hanya satu** angka yang boleh bergerak pada satu waktu. Kalau harga lama masih
beranimasi saat harga baru masuk, penonton tidak tahu mana yang harus dibaca.

---

## Resep D — `kinetic-claim` (typographic, tanpa footage)

Cocok untuk 6–9 detik, tanpa narasi.

* 1 kalimat dipecah 3 baris, muncul per baris (interval 8f).
* Setiap baris: `maskUp` 16f, bukan fade — mask memberi rasa "diukir".
* Baris terakhir: scale 1.06 → 1 dalam 10f + warna aksen pada 1 kata.
* Latar: bg + 1 shape bergerak lambat (translate ±20px, 120f, linear).

---

## Resep E — `before-after`

Split layar vertikal: 2 scene berbagi waktu.

```
panel_kiri  : x -270 (setengah kiri), clip 0
panel_kanan : x +270
divider     : shape line, tinggi 0 → 100% (18f), lalu label "VS" popIn
```

Transisi: divider wipe dari tengah, kedua panel bergeser 40px saling menjauh (dur 16f).

---

## Palette & type default (ads)

| Token | Nilai | Catatan |
| --- | --- | --- |
| bg | `#0B0B10` | hampir hitam, bukan hitam (#000 bikin banding di OLED) |
| aksen | `#7C5CFF` (ungu) / `#FF5C7A` (merah) / `#2EE6A8` (hijau) | pilih **satu** |
| teks | `#FFFFFF` | |
| muted | `#9A9AAC` | untuk subline, label |
| headline | 96–150 px, weight 800–900, letter-spacing -2..-4 | |
| subline | 36–46 px, weight 500 | |
| label | 26–34 px, weight 600–700, letter-spacing +6 | kapital |

---

## Kesalahan paling sering di kategori ads

1. Terlalu banyak teks di beat 1 (hook harus ≤ 5 kata).
2. CTA tidak pernah diam — selalu ada gerakan, jadi mata tidak bisa "klik" secara mental.
3. Semua elemen pakai easing berbeda → terasa acak.
4. Tidak ada end_fade → video berhenti mendadak saat di-loop (TikTok loop otomatis, jadi
   fade-out ke warna bg penting).
5. Counter berhenti di angka "aneh" (misal 69.7%) karena easing belum clamp — validator
   memastikan `to_value` tercapai pada frame terakhir grow.
