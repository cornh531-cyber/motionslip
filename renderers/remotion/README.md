# Remotion

Build: `python3 cli/motion.py build scene.json --target remotion --out out/Nama`
Hasil: `out/Nama/remotion/` (project siap `npm install`).

## Kontrak

| Kebutuhan | Cara |
| --- | --- |
| Waktu | `const frame = useCurrentFrame()` — integer |
| Durasi | `<Composition durationInFrames>` = `composition.durationInFrames` |
| Nilai animasi | fungsi murni: `track(frame, keys)` (disediakan `src/lib/motion.ts`) |
| Aset | `staticFile('logo.png')` → folder `public/` |
| Video | `<OffthreadVideo src={staticFile('...')} />` |

## Versi minimal yang benar

```tsx
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {track} from './lib/motion';

export const Demo: React.FC = () => {
  const f = useCurrentFrame();
  const t = f - 15;                                  // layer mulai frame 15
  const opacity = track(t, [{s:0,d:12,f:0,v:1,e:'easeOutCubic'}], 1);
  const y = track(t, [{s:0,d:18,f:56,v:0,e:'easeOutQuint'}], 0);
  return (
    <AbsoluteFill style={{backgroundColor: '#0B0B10'}}>
      <div style={{position:'absolute', left:'50%', top:'50%', color:'#fff',
                   fontSize:120, fontWeight:900, opacity,
                   transform:`translate(-50%,-50%) translateY(${y}px)`}}>
        HALO
      </div>
    </AbsoluteFill>
  );
};
```

`lib/motion.ts` menyediakan:
- `track(frame, keys, base)` — interpolasi keyframe; keyframe belakangan menang.
- `counter(frame, start, dur, from, to, ease, decimals)` — angka naik.
- `grow(frame, start, dur)` — progress 0..1 untuk bar chart.
- `inset(t,r,b,l)` — helper clip-path.

## Anti-pattern

```tsx
// ❌ tidak deterministik
const opacity = Math.random() > 0.5 ? 1 : 0.4;

// ❌ wall clock — hasil render berbeda tiap run
const [v, setV] = useState(0);
useEffect(() => { setTimeout(() => setV(1), 300); }, []);

// ✅ selalu dari frame
const opacity = track(frame, [{s:0,d:12,f:0,v:1,e:'easeOutCubic'}], 1);
```

## Render

```bash
npm install
npm run dev                     # studio
npm run render                  # mp4
npm run render:gif              # gif
npx remotion still src/index.ts AdsFlashSale out/still.png --frame=120
```

Lisensi Remotion terpisah dari lisensi skill ini (gratis untuk individu / tim ≤ 3 orang).
