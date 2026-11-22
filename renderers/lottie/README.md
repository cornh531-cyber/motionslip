# Lottie / dotLottie

Skill ini **tidak** meng-generate Lottie secara langsung (format keyframe-nya berbasis persen
dengan struktur transform hierarkis yang sangat berbeda). Jalur yang disarankan:

## Opsi A — via After Effects (paling akurat)

1. Bangun komposisi di AE dengan timing dari `scene.json`
   (frame scene = frame AE, timeline identik).
2. Ekspor dengan **Bodymovin** → `data.json`.
3. Optimasi: `npx lottie-optimizer` atau [lottie.app](https://lottiefiles.com/).

## Opsi B — via SVG + CSS (Lottie-like, tanpa AE)

CSStarget (`--target preview`) menghasilkan HTML+JS murni. Untuk animasi SVG di web/app,
pakai pola keyframe yang sama:

| scene.json | Lottie (JSON) |
| --- | --- |
| `frame` | `t` (frame), durasi `op` dalam frame |
| `easeOutCubic` | `o: {x:[0.33], y:[1]}, i: {x:[0.68], y:[0]}` |
| `opacity` | transform `o` (0–100) |
| `x`/`y` (offset dari tengah) | transform `p` (posisi absolut) |
| `scale` | transform `s` (persen) |
| `clipTop` dll | mask / trim path (butuh layer mask terpisah) |

Konversi manual: `t_lottie = frame`, `op = durationInFrames`, `o/i` diambil dari
`presets/easings.json` → kolom `css` (cubic-bezier).

## Opsi C — dotLottie untuk app mobile

Setelah punya `data.json`: `npx @dotlottie/cli convert data.json` → `.lottie`
(ukuran 50–80% lebih kecil, mendukung theme & state machine).

## Kapan Lottie tepat?

- Ikon/ilustrasi kecil yang di-loop di UI.
- Overlay ringan di aplikasi (bukan video penuh).
Untuk video penuh 1080×1920 dengan teks panjang, Remotion/HyperFrames lebih efisien.
