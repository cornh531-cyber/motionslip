# Renderers

Folder ini menjelaskan **kontrak tiap engine** + contoh kode minimal yang benar.
Kode produksi tidak disimpan di sini — ia **digenerate** oleh `cli/motion.py build` ke
`out/<Nama>/<renderer>/`, supaya selalu sinkron dengan scene.

| Folder | Engine | Model waktu | Bahasa |
| --- | --- | --- | --- |
| `remotion/` | Remotion 4.x | frame (`useCurrentFrame`) | TSX |
| `hyperframes/` | HyperFrames (HeyGen) · OpenMotion | detik (`data-start`) | HTML + GSAP |
| `motion-canvas/` | Motion Canvas | detik (generator) | TS |
| `lottie/` | Lottie / dotLottie / AE | persen (0–100) | JSON |
| `css/` | HTML + CSS/WAAPI | detik | HTML |

## Prinsip yang sama di semua engine

1. **Seekable**: renderer harus bisa melompat ke frame mana pun tanpa memutar dari 0.
2. **Deterministik**: input sama → output sama, byte per byte.
3. **Tanpa wall-clock**: `Date.now()`, `performance.now()`, `setTimeout` = haram di komposisi.
4. **Satu sumber kebenaran**: timing berasal dari `scene.json`, bukan diketik ulang manual.
