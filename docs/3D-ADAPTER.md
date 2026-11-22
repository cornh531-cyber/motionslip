# 3D Adapter — kalau brief-nya benar-benar minta 3D

`scene.json` adalah format **2D/2.5D**. Itu keputusan desain, bukan kekurangan: 2D transform
cukup untuk ~90% motion graphics kategori "3D" di media sosial, dan hasilnya deterministik di
semua engine.

Kalau butuh lebih, ada tiga jalur. Semua tetap memakai skill ini untuk timing & tipografi.

---

## Jalur 1 — CSS perspective (paling murah, tanpa engine baru)

Cocok untuk: rotateX/rotateY pada kartu, kubus sederhana, tilt 3D teks.

Di **HyperFrames** (HTML), tambahkan layer manual:

```html
<div class="clip" data-start="1" data-duration="4" data-track-index="3"
     style="perspective: 900px; position:absolute; left:50%; top:50%; transform:translate(-50%,-50%)">
  <div id="cube" style="width:260px;height:260px;background:#FF5C7A;border-radius:24px;
       transform-style:preserve-3d"></div>
</div>
<script>
  const tl = gsap.timeline({paused: true});
  tl.fromTo('#cube',
    {rotationY: -35, rotationX: 18, transformPerspective: 900},
    {rotationY: 35, rotationX: -6, duration: 3, ease: 'power2.inOut'}, 1);
  window.__timelines['NamaScene'] = tl;   // gabungkan dengan timeline hasil generate
</script>
```

Di **Remotion** (React): style `{transform: 'perspective(900px) rotateY(20deg)'}` dengan nilai
dari `track(frame, ...)`. Tetap deterministik.

Batas: tanpa lighting, tanpa occlusion, tanpa depth of field.

---

## Jalur 2 — Three.js di dalam komposisi

Cocok untuk: objek 3D asli, material, lighting, kamera.

**Remotion**: `@remotion/three` (`<ThreeCanvas>`) — nilai kamera/objek harus fungsi dari
`frame`, jangan dari `clock`.

```tsx
import {ThreeCanvas} from '@remotion/three';
import {useCurrentFrame, useVideoConfig} from 'remotion';

const frame = useCurrentFrame();
const rotY = (frame / fps) * 0.6;         // radian per detik — linear, aman
<ThreeCanvas width={1920} height={1080}>
  <mesh rotation={[0.2, rotY, 0]}>
    <boxGeometry args={[2, 2, 2]} />
    <meshStandardMaterial color="#FF5C7A" />
  </mesh>
  <ambientLight intensity={0.6} />
  <directionalLight position={[3, 5, 2]} intensity={1.2} />
</ThreeCanvas>
```

**HyperFrames**: adapter Three.js resmi tersedia (semua animasi harus seekable). Render
loop Three.js harus di-*advance* manual per frame — jangan pakai `requestAnimationFrame`.

---

## Jalur 3 — render offline (paling aman & paling mahal)

Cocok untuk: produk hero, simulasi, particle, apa pun yang butuh kualitas render film.

```
Blender / Spline / Cinema4D
   → render PNG sequence (30 fps, 1920×1080, alpha kalau perlu)
   → ffmpeg: PNG → mp4 (prores / h264)
   → masukkan sebagai layer footage di scene
```

Timing tetap dari skill ini: footage menempati `from`/`durationInFrames` tertentu, dan teks/CTA
di sekitarnya tetap memakai aturan smooth yang sama.

Di Remotion: `<OffthreadVideo src={staticFile('product.mp4')} />` atau `<Img src={staticFile('frames/f001.png')} />`.
Di HyperFrames: `<video class="clip" data-start="0" data-duration="6" src="assets/product.mp4">`.

---

## Memilih jalur

| Kebutuhan | Jalur |
| --- | --- |
| Tilt / kubus / kartu 3D | 1 (CSS perspective) |
| Objek 3D dengan material & cahaya, waktu render < 1 jam | 2 (Three.js) |
| Kualitas iklan TV, banyak objek, simulasi | 3 (offline render) |
| 2.5D orb/ring (mayoritas konten sosial) | **scene.json** — tidak perlu adapter |

---

## Kontrak yang tidak boleh dilanggar jalur mana pun

1. Nilai 3D = fungsi dari `frame` (bukan waktu nyata).
2. Rotasi kontinu boleh `linear`; masuk/keluar kamera tetap pakai easing.
3. Tidak ada `Math.random()` tanpa seed — kalau butuh variasi, pakai hash deterministik:
   `rand(i) = fract(sin(i * 12.9898) * 43758.5453)`.
4. Render 3D harus punya fps yang sama dengan komposisi (30 fps → render 30 fps).
