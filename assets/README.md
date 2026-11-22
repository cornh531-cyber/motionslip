# assets/

Folder untuk asetmu: logo, gambar produk, footage, audio.

Konvensi:

```
assets/
├── logo.png
├── product.mp4
└── bgm.mp3
```

Referensi di scene:

```json
{ "id": "logo", "type": "image", "src": "assets/logo.png", "w": 320, "h": 320, "fit": "contain" }
```

Catatan per engine:

| Target | Cara aset dipakai |
| --- | --- |
| preview | path relatif terhadap `preview.html` → letakkan di folder yang sama atau ubah `src` |
| HyperFrames | path relatif terhadap `index.html` (salin `assets/` ke sampingnya) |
| Remotion | pindahkan ke `public/` dan rujuk tanpa prefix `public/` (generator sudah menulis `staticFile(...)`) |
| Motion Canvas | path relatif dari `src/scenes/` (generator menulis `../assets/...`) |

Jangan menaruh aset milik creator video referensi di sini. Lihat `NOTICE`.
