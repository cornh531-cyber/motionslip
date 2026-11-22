# FAQ

**Apakah skill ini benar-benar "mengubah" video TikTok jadi skill?**
Link direferensikan (URL kanonik + creator + video id sudah di-resolve otomatis), lalu
diterjemahkan menjadi **grammar motion + resep + scene siap render**. Isi frame-per-frame tiap
video belum di-ingest karena TikTok memblokir fetch non-browser. Prosedur melengkapinya ada di
`docs/WORKFLOW-reference-to-motion.md`. Skill tetap 100% fungsional tanpa itu: yang dipakai
adalah resep + validator, bukan copy video.

**Kenapa harus ada format scene sendiri, tidak langsung Remotion?**
Karena satu brief biasanya butuh lebih dari satu engine (preview di browser, render di
Remotion atau HyperFrames). Format perantara juga membuat validator bisa menegakkan aturan
smooth tanpa bergantung pada engine.

**Apakah hasilnya "smooth" benar-benar dijamin?**
Tidak ada yang bisa menjamin rasa. Yang dijamin: **tidak ada pelanggaran teknis** yang biasanya
membuat animasi terasa patah (durasi terlalu pendek, easing linear pada gerak masuk, keyframe
tumpang tindih, frame kosong, overflow teks). Skor 85+ = bebas pelanggaran umum.

**Bisa dipakai untuk video landscape / square?**
Ya. Ubah `composition.width/height`: 1920×1080, 1080×1080, 1080×1350, 3840×2160.
Pakai `presets/tokens.json → safeArea` sebagai acuan margin.

**Fps 60?**
Didukung (24/25/30/50/60). Semua durasi otomatis dihitung ulang jika kamu mengubah fps?
Tidak — durasi tetap dalam frame. Kalau ganti fps, kalikan durasi dengan `fps_baru/fps_lama`
untuk mempertahankan durasi detik.

**Ada audio?**
Spec ini fokus visual. Tambahkan audio setelah render (FFmpeg) atau lewat engine:
Remotion `<Audio>`, HyperFrames `<audio class="clip" data-start>`. Beat musik sebaiknya
menentukan `from` tiap layer — kalau user punya track, minta BPM-nya lalu hitung
`frame_per_beat = fps * 60 / bpm`.

**Kenapa `linear` dilarang kecuali rotasi?**
Karena otak membaca percepatan. Gerak konstan terasa mekanis dan murah. Rotasi kontinu adalah
pengecualian karena tidak punya awal/akhir.

**Bisakah agen local model (7B) memakai ini?**
Ya, dengan pola "salin template, ubah teks & warna". Validator jadi jaring pengaman.
Lihat `config/models.json`.

**Bagaimana kalau saya butuh 3D mesh nyata?**
Bukan domain spec ini. Render di Blender/Spline/Three.js → ekspor footage → pasang sebagai
layer `image`/video. Lihat `docs/3D-ADAPTER.md`.

**Boleh dipakai komersial?**
Skill: Apache-2.0 (ya, sertakan `NOTICE`). Engine: ikuti lisensi masing-masing (Remotion &
GSAP punya ketentuan sendiri). Aset referensi: milik creator.

**Bagaimana cara kontribusi / menambah resep?**
Tambahkan resep baru ke `references/taxonomy-*.md`, lalu buat contoh di `examples/` dan pastikan
`python3 cli/motion.py validate examples/<baru>.scene.json` hijau (skor ≥ 85).
