# Smooth Motion — aturan yang bikin animasi terasa mahal

> Dokumen paling penting di skill ini. Kalau agen hanya membaca satu file, baca ini.
> Semua angka di sini sudah di-encode ke `cli/core.py` (validator) supaya tidak bisa "lupa".

Animasi yang terasa *smooth* bukan animasi yang banyak. Animasi smooth = **gerak yang
disengaja**: satu properti bergerak pada satu waktu, easing yang tepat, dan durasi yang
konsisten. 90% video motion graphics yang terlihat amatir melanggar 5 hal di bawah ini.

---

## 1. Frame budget (angka keramat)

Pada 30 fps, 1 frame = 33,3 ms. Angka di bawah adalah batas di mana mata manusia
mulai "melihat" animasinya, bukan hasilnya.

| Kejadian | Frame @30fps | Detik | Catatan |
| --- | --- | --- | --- |
| Persepsi instan | 1–2 | 0.03–0.07 | cuma untuk *state change*, bukan animasi |
| Micro-interaction (hover, pulse) | 4–8 | 0.13–0.27 | harus terasa "snap" |
| Fade masuk teks | 10–16 | 0.33–0.53 | di bawah 8f = kedip |
| Slide masuk elemen | 14–20 | 0.47–0.67 | jarak 32–120 px |
| Animasi hero / headline | 20–30 | 0.67–1.0 | boleh pakai `easeOutQuint`/spring |
| Transisi antar scene | 8–16 | 0.27–0.53 | overlap, bukan hitam dulu |
| Logo sting penuh | 45–90 | 1.5–3.0 | ada antisipasi + settle |
| Baca 1 baris teks | 45+ | 1.5+ | **ini bukan animasi, ini keterbacaan** |
| Ganti shot / beat iklan | 60–150 | 2–5 | tiap 2–5 detik harus ada perubahan |

**Aturan turunan:** kalau sebuah elemen butuh lebih dari 1 detik untuk masuk, penonton
sudah "selesai" membacanya sebelum animasinya selesai. Pecah jadi 2 langkah
(mask → slide) atau perpendek.

---

## 2. Easing: kapan pakai apa

Default yang salah = `linear`. `linear` hanya benar untuk gerak kontinu tanpa awal-akhir:
rotasi loop, progress bar, marquee.

| Situasi | Easing | Alasan |
| --- | --- | --- |
| Masuk dari luar frame | `easeOutQuint` / `easeOutExpo` | cepat di awal, pelan saat mendarat → terasa berat & mahal |
| Fade sederhana | `easeOutCubic` | cukup, tidak menarik perhatian |
| Pop / stamp / badge | `easeOutBack` (overshoot 1.7) | memberi "pantulan" kecil |
| Elemen kartun / playful | `easeOutElastic` | hati-hati: hanya untuk 1–2 elemen |
| Keluar | `easeInCubic` | percepatan menghilang, tidak "ditarik" |
| Transform dua arah (A→B→A) | `easeInOutCubic` | simetris |
| Follow-through mekanis | `springSnappy` | overshoot 2–4%, settle < 6 frame |
| Kamera / parallax | `linear` atau `easeInOutQuad` | gerak kontinu |

**Gabungan yang sering dipakai (recipe "slide up premium"):**

```
opacity : 0 → 1  selama 12f, easeOutCubic
y       : 56 → 0 selama 18f, easeOutQuint
```

Opacity selesai lebih dulu daripada gerak. Hasilnya elemen terasa "muncul lalu mendarat",
bukan "muncul sambil melayang". Ini yang membedakan pro vs template gratisan.

---

## 3. Satu properti, satu cerita

Jangan animasikan `opacity + y + scale + rotate + blur` sekaligus. Pilih **satu** properti
utama (gerak) + **satu** pendukung (opacity). Lebih dari itu = noise.

| Kombinasi | Efek psikologis |
| --- | --- |
| opacity + y | masuk netral, paling aman, 80% kasus |
| opacity + scale (0.92→1) | "zoom halus", terasa fokus |
| opacity + scale (0.6→1, back) | pop, playful, iklan diskon |
| clip + y | reveal sinematik (mask up) |
| opacity + blur | dreamy, untuk transisi antar dunia |

---

## 4. Stagger: ritme, bukan tumpukan

Stagger = memberi jeda tetap antar item yang sama jenisnya.

| Item | Interval | Total durasi masuk |
| --- | --- | --- |
| 3–5 kata headline | 2–4f | ≤ 30f |
| 3 bullet point | 6–10f | ≤ 45f |
| 5–8 bar chart | 3–5f | ≤ 40f |
| Grid ikon 9+ | 1–2f | ≤ 30f |

Aturan: **total stagger + durasi tween ≤ waktu baca**. Kalau 8 item × 5f = 40f hanya untuk
memulai item terakhir, penonton sudah pindah perhatian. Percepat interval, jangan perpanjang tween.

Arah stagger harus punya alasan: kiri→kanan (membaca), atas→bawah (daftar), luar→dalam (fokus).

---

## 5. Kontinuitas & kontinuitas visual

* **Jangan pernah ada frame kosong.** Kalau layer A selesai di frame 100 dan layer B mulai
  di frame 110, penonton melihat 10 frame kosong = "kedip". Overlap 6–10 frame.
  Validator menandai celah ≥ 1 detik (lihat `validate`).
* **Antisipasi** (gerak kecil ke arah berlawanan sebelum bergerak) menambah 6–10 frame tapi
  membuat gerak terasa punya massa. Hanya dipakai di hero, bukan semua elemen.
* **Follow-through**: setelah elemen mendarat, beri 1 gerakan kecil yang menyusul
  (badge yang ikut bergeser sedikit). Maksimum 1 gerakan susulan.
* **Momentum**: semua elemen di scene sebaiknya bergerak searah (mis. semua dari bawah).
  Campur atas+bawah dalam satu beat = berantakan.

---

## 6. Tipografi bergerak

* **Line-height 0.95–1.05** untuk headline besar; 1.2–1.4 untuk body.
* **Letter-spacing negatif** (-2 s/d -4 px) untuk ukuran > 100 px, positif (+4 s/d +8) untuk
  label kecil kapital.
* **Per-kata**, bukan per-huruf — kecuali untuk efek mesin/terminal.
* **Hindari animasi per-huruf dengan `blur`** → sangat mahal dan terlihat "smear".
* Teks yang bergerak harus **mendarat sebelum** orang mulai membaca: beri ≥ 30 frame diam
  setelah animasi masuk sebelum elemen berikutnya bergerak.
* **Safe area**: TikTok/Reels memotong ±120 px atas dan ±250 px bawah pada 1080×1920.
  Jangan taruh teks penting di sana (skill ini default ke tengah).

---

## 7. Warna & cahaya bergerak

* Satu aksen saja (> 2 warna = template Canva). Aksen dipakai untuk 1 kata, 1 tombol, 1 garis.
* Glow = `blur` besar + opacity 0.35–0.55, jangan pernah 1.0 (menghabiskan kontras).
* Gradient bergerak harus `linear` dan lambat (≥ 3 detik), kalau tidak jadi distraksi.
* Jangan animasikan warna teks (mahal dibaca); animasikan **posisi** atau **mask**-nya.

---

## 8. Komposisi & kamera

| Gerakan kamera | Aman untuk | Bahaya |
| --- | --- | --- |
| Slow push-in (scale 1 → 1.04, ≥ 3 s) | semua | terlalu cepat = mual |
| Micro-shake | impact / bass drop | > 4 px = terlihat rusak |
| Parallax 2 layer | edukasi, chart | 3+ layer = berat |
| Whip pan | transisi cepat | butuh motion blur |

Fokus: satu elemen dominan, satu pendukung, satu latar. Kalau semua elemen punya animasi
masuk, tidak ada yang dominan → mata bingung, video terasa "ramai tapi kosong".

---

## 9. Performa & determinisme (khusus video-as-code)

1. **Jangan pernah** `Math.random()` tanpa seed — frame ke-30 di render pertama harus sama
   dengan frame ke-30 di render kedua. HyperFrames mensyaratkan timeline *seekable* & paused.
2. **Jangan** animasi berbasis waktu nyata (`setTimeout`, `requestAnimationFrame`) di dalam
   komposisi. Semua nilai = fungsi dari frame.
3. Font harus sudah dimuat sebelum frame 0 (FOUT membuat teks "loncat" di tengah render).
4. `blur` besar dan `box-shadow` besar memperlambat render secara linear — pakai hanya di
   layer statis atau elemen kecil.
5. Video/gambar besar: pakai `staticFile()` (Remotion) atau path relatif (HyperFrames), jangan
   data-URI raksasa yang bikin bundle 50 MB.

---

## 10. Checklist final (10 detik sebelum render)

- [ ] Tidak ada easing `linear` kecuali rotasi/progress
- [ ] Tidak ada animasi < 4 frame
- [ ] Setiap elemen punya waktu diam ≥ 20 frame sebelum elemen berikutnya bergerak
- [ ] Tidak ada frame tanpa konten (cek `motion.py validate`)
- [ ] Satu elemen dominan per beat
- [ ] Teks muat di safe area (1080×1920 → margin 120 atas, 250 bawah)
- [ ] Total durasi = kelipatan beat (2–5 detik per ide)
- [ ] Skor `motion.py validate` ≥ 85

---

## Skala rasa (buat kalibrasi cepat)

| Skor | Artinya |
| --- | --- |
| 95–100 | Siap tayang. Timing & easing konsisten. |
| 85–94 | Layak render, ada 1–2 detail yang bisa dipoles. |
| 60–84 | Ada animasi terlalu pendek / celah / easing mekanis. Tonton ulang. |
| < 60 | Jangan render. Perbaiki struktur dulu (durasi, overlap, jumlah properti). |
