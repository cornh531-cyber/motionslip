# Taxonomy — Video 3D (3d)

20 referensi TikTok di `catalog.json` → kategori `3d`.

Dua hal yang harus dipisahkan sejak awal:

1. **Motion 3D nyata** (mesh, lighting, kamera perspektif) → butuh renderer 3D:
   Three.js (via adapter HyperFrames/Remotion), Blender → PNG sequence, atau Spline.
2. **Motion "3D-look" 2.5D** (pseudo-3D dengan 2D transform) → bisa 100% di spec ini:
   rotasi, scale, blur, layer parallax, gradient. Ini yang dilakukan `examples/3d.scene.json`.

90% video "3D" di TikTok kategori ini sebenarnya **2.5D**: teks besar + orb/ring berputar +
glow + motion blur. Skill ini menyediakan keduanya.

---

## Resep A — `orbital-showcase` (2.5D, tanpa mesh)

Implementasi: `examples/3d.scene.json` (1920×1080, 10s).

```
0.0s  bg fade 10f
0.0s  halo: circle 760px, blur 180px, opacity .45, scaleIn 40f easeOutQuint
0.2s  ring_outer: circle stroke 2px, fade 24f + rotate 0→360 linear 294f (loop)
0.5s  ring_inner: circle stroke 1px, rotate 360→0 linear (arah berlawanan = kedalaman)
0.7s  core: rect radius 44, popIn 26f easeOutBack + rotate 0→90 easeOutBack 60f
1.2s  title: stagger 4f slideUp 22f, 1 kata aksen
2.7s  price counter: slideUp 20f + grow 34f
2.0s  handle (pojok): fade 20f delay 20f
9.5s  end_fade 14f
```

Kunci rasa 3D tanpa 3D:
* **Dua orbit berlawanan arah** → otak membaca kedalaman.
* **Glow besar di belakang objek** → objek terasa "menyala", bukan ditempel.
* **Satu objek padat (core) + dua garis tipis (ring)** → hirarki fokus jelas.
* Rotasi **harus linear** — ini satu-satunya pemakaian `linear` yang benar untuk rotasi kontinu.
* Jangan beri `easeOutBack` pada rotasi kontinu; hasilnya "tersendat".

---

## Resep B — `product-reveal` (footage-based)

Kalau kamu punya footage produk (mp4) atau render Blender:

| Layer | Timing | Catatan |
| --- | --- | --- |
| footage | 0–180 | di-*scale* 1.06 → 1 (120f, linear) → gerak kamera halus |
| vignette | 0–180 | shape radial/gradient, opacity .35 |
| title | 40 | maskUp 18f, di atas footage |
| price | 90 | counter |
| cta | 140 | pill |

Untuk target Remotion: `<OffthreadVideo>` / `<Video>`; HyperFrames: `<video class="clip">` atau
clip video dengan `data-start`. Validator tetap sama karena timing-nya di scene JSON.

---

## Resep C — `kinetic-3d-type`

Teks besar yang "berputar" di ruang:

```
baris 1: rotateX tidak tersedia di spec → gunakan scaleY 1.15 → 1 + blur 8 → 0 (18f)
baris 2: maskUp 16f + y 40 → 0
```

Kalau kamu butuh rotasi perspektif sungguhan (rotateX/rotateY), lihat
`docs/3D-ADAPTER.md` — ada dua jalan: (a) CSS `perspective` + `transform: rotateY()` lewat
custom layer di HyperFrames/Remotion, (b) Three.js adapter.

---

## Resep D — `loop-sting` (logo 3–5 detik, bisa di-loop mulus)

Syarat loop mulus: **frame terakhir = frame pertama** (nilai properti sama).

```
0f    scale .8, opacity 0, blur 12
12f   scale 1.02, opacity 1, blur 0     (easeOutQuint)
20f   scale 1.00                         (settle)
60f   rotate ring 0 → 360 (linear, tapi nilai sama di akhir = tidak terlihat loop)
90f   semua kembali ke nilai frame 0 (fade 12f)
```

Validator tidak bisa mendeteksi loop-mulus secara otomatis — **cek manual**: nilai tiap track
pada frame `dur-1` harus mendekati nilai pada frame `0`.

---

## Angka yang bikin 3D terasa mahal

| Parameter | Nilai aman |
| --- | --- |
| Glow blur | 120–200 px (jangan < 60) |
| Glow opacity | 0.35–0.55 |
| Stroke ring | 1–2 px (bukan 4) |
| Rotasi loop | 240–360 frame per putaran (jangan < 120 → mual) |
| Push-in kamera | scale 1 → 1.03..1.06 dalam ≥ 90f |
| Motion blur | hanya jika kecepatan > 1500 px/s |
| Jumlah elemen berputar | maksimum 2 |

---

## Limitasi spec (jujur)

| Fitur 3D | Dukungan di `scene.json` | Workaround |
| --- | --- | --- |
| Rotasi sumbu Z | ✅ `rotate` | — |
| Rotasi X/Y (perspektif) | ❌ | CSS `perspective` custom / Three.js |
| Mesh & lighting | ❌ | render di Blender/Spline → footage |
| Depth of field | ⚠️ | blur per layer |
| Motion blur | ❌ (native) | blur berbasis velocity di renderer |
| Shadow / ambient occlusion | ❌ | bake di render 3D |

Kalau brief-nya benar-benar butuh objek 3D, jalur yang benar bukan memaksa spec ini, tapi:
**render 3D di Blender/Spline → ekspor PNG sequence / mp4 → pasang sebagai layer footage**.
Skill ini tetap mengurus timing, tipografi, dan CTA di sekitarnya.

---

## Palette & type default (3d)

| Token | Nilai |
| --- | --- |
| bg | `#05060B` |
| aksen | `#FF5C7A` / `#7C5CFF` / `#00D8FF` |
| teks | `#FFFFFF` |
| muted | `#8E93A6` |
| headline | 130–180 px, weight 900, line-height 0.95 |
