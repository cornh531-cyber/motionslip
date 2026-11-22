# HyperFrames / OpenMotion

Build: `python3 cli/motion.py build scene.json --target hyperframes --out out/Nama`

HyperFrames (HeyGen, Apache-2.0) merender HTML + animasi **seekable** menjadi MP4 lewat
headless Chrome + FFmpeg. OpenMotion (Clawnify) memakai engine yang sama dengan UI timeline.

## Kontrak wajib

| Elemen | Atribut / API |
| --- | --- |
| Root komposisi | `data-composition-id`, `data-width`, `data-height`, `data-fps`, `data-duration` (detik) |
| Setiap elemen bertiming | `class="clip"` + `data-start`, `data-duration`, `data-track-index` (semua **detik**) |
| Timeline | satu `gsap.timeline({paused: true})` |
| Registrasi | `window.__timelines["<composition-id>"] = tl` |
| Larangan | `Math.random`, `Date.now`, animasi yang tidak bisa di-`seek` |

## Versi minimal yang benar

```html
<div id="stage"
     data-composition-id="Demo"
     data-width="1080" data-height="1920" data-fps="30" data-duration="5">
  <div class="clip" data-start="0.5" data-duration="4" data-track-index="1"
       style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)">
    <div id="title" style="font:900 120px Inter;color:#fff">HALO</div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>
  const tl = gsap.timeline({paused: true});
  tl.fromTo('#title', {opacity: 0, y: 56},
                      {opacity: 1, y: 0, duration: 0.6, ease: 'power4.out'}, 0.5);
  window.__timelines = {Demo: tl};
</script>
```

## Mapping dari scene.json

| scene | HyperFrames |
| --- | --- |
| `frame / fps` | `data-start` (detik) |
| `durationInFrames / fps` | `data-duration` |
| `track` | `data-track-index` |
| `easeOutQuint` | `ease: "power4.out"` (lihat `cli/jsassets.py → GSAP_EASE_MAP`) |
| `clipTop/Right/Bottom/Left` | CSS var `--ct/--cr/--cb/--cl` di `clip-path: inset(...)` |
| `counter` | tween proxy object + `onUpdate` (tetap seekable) |
| `chart` | tween `scaleY` per bar |

## Perintah

```bash
npx hyperframes check .                          # validasi
npx hyperframes preview                          # studio + live reload
npx hyperframes render --quality high -o ad.mp4  # render lokal
npx hyperframes cloud render                     # render di cloud HeyGen
npx hyperframes doctor                           # cek Node 22+ & FFmpeg
```

OpenMotion: salin isi `index.html` sebagai composition baru; engine-nya HyperFrames sehingga
`data-*` dan `window.__timelines` langsung dikenali.
