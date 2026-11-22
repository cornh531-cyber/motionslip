# CSS / WAAPI (HTML murni)

Target `preview` menghasilkan satu file HTML mandiri (tanpa CDN, tanpa npm) yang:

- menggambar semua layer dengan DOM + inline style,
- menghitung nilai per frame dari keyframe scene (`track()` yang sama dengan validator),
- punya scrub bar, timeline clip, play/pause, loop, dan keyboard shortcut
  (`space`, `←`, `→`).

File ini **bukan** video — ia adalah *frame reviewer*: alat untuk memastikan timing sebelum
render mahal. Karena itu preview dipakai di loop kerja (`validate → build preview → review`).

## Mau embed animasi yang sama di landing page?

Gunakan `presets/easings.json` (kolom `css`) + keyframe eksplisit:

```css
@keyframes slideUpPremium {
  0%   { opacity: 0; transform: translateY(56px); }
  100% { opacity: 1; transform: translateY(0); }
}
.hero-title {
  animation: slideUpPremium 600ms cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: 200ms;   /* = frame 6 @30fps */
}
```

Aturan: `both` wajib (mempertahankan state akhir), dan jangan pakai `animation-iteration-count`
untuk elemen yang seharusnya berhenti.

## WAAPI (lebih presisi)

```js
el.animate(
  [{opacity: 0, transform: 'translateY(56px)'}, {opacity: 1, transform: 'translateY(0)'}],
  {duration: 600, delay: 200, easing: 'cubic-bezier(0.22,1,0.36,1)', fill: 'both'}
);
```

Untuk website, WAAPI lebih mudah di-seek (`anim.currentTime = ms`) sehingga mirip model
scene ini.
