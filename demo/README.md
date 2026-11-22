# demo/

Bukti bahwa skill ini jalan — tiga scene bawaan, hasil build apa adanya.

| File | Scene | Canvas | Durasi | Skor |
| --- | --- | --- | --- | --- |
| `ads-preview.html` | `examples/ads.scene.json` | 1080×1920 | 15.0 s | 100/100 |
| `education-preview.html` | `examples/education.scene.json` | 1080×1920 | 18.0 s | 100/100 |
| `3d-preview.html` | `examples/3d.scene.json` | 1920×1080 | 10.0 s | 100/100 |

Buka file HTML-nya langsung di browser: ada play/pause, scrub bar, timeline clip
(warna = track), riwayat frame, dan loop. Semua mandiri — tanpa CDN, tanpa `npm install`,
tanpa server. Itulah yang dipakai untuk **frame review** sebelum render mahal.

`still/*.png` = satu frame dari masing-masing scene, dirender dengan renderer QA internal
(bukan engine final): font fallback, highlight multi-warna dan blur belum seakurat
`preview.html` / Remotion. Anggap ini sebagai *thumbnail*, bukan hasil akhir.

Bikin ulang kapan saja:

```bash
python3 cli/motion.py build examples/ads.scene.json --target preview --out demo-tmp
```
