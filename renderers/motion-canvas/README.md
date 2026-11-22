# Motion Canvas

Build: `python3 cli/motion.py build scene.json --target motion-canvas --out out/Nama`

Motion Canvas memakai **generator** (`yield*`) dengan waktu dalam **detik**, bukan model
"nilai = f(frame)". Compiler menerjemahkan timeline absolut menjadi tween paralel yang
masing-masing diawali `waitFor(start)` — hasil visualnya setara, tapi kodenya bergaya
sekuensial.

## Versi minimal yang benar

```ts
import {makeScene2D, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutCubic, easeOutQuint, waitFor} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  view.fill('#0B0B10');
  const title = createRef<Txt>();
  view.add(<Txt ref={title} text="HALO" fontSize={120} fontWeight={900} fill="#fff" />);
  title().opacity(0);

  yield* all(
    (function* () { yield* waitFor(0.5); yield* title().opacity(1, 0.4, easeOutCubic); })(),
    (function* () { yield* waitFor(0.5); yield* title().y(56, 0).to(0, 0.6, easeOutQuint); })(),
  );
  yield* waitFor(2);
});
```

## Yang bisa & tidak bisa

| Fitur | Status |
| --- | --- |
| opacity, x, y, scale, rotation | ✅ tween penuh |
| counter | ✅ `createSignal` + `text={() => ...}` |
| chart | ✅ bar `scale.y` |
| clip / mask (`maskUp`, `wipeRight`) | ⚠️ tidak ada padanan core → diberi komentar TODO |
| blur | ⚠️ butuh plugin/filter |

Kalau brief butuh mask/blur secara presisi, target **Remotion** atau **HyperFrames** lebih tepat.
