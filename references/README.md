# References

Folder ini menyimpan **katalog 60 video referensi** (TikTok) + hasil "pembacaan" motion-nya.

| File | Isi |
| --- | --- |
| `catalog.json` | 60 entri: id, kategori, creator, short URL, URL kanonik, video id, status ingest |
| `catalog.md` | versi tabel (enak dibaca manusia) |
| `taxonomy-ads.md` | grammar + 5 resep untuk video iklan |
| `taxonomy-education.md` | grammar + 5 resep untuk video edukasi |
| `taxonomy-3d.md` | grammar + 4 resep 2.5D + limitasi 3D nyata |
| `smooth-motion.md` | aturan timing/easing yang dipakai validator |

## Status ingest (penting, jujur)

Link TikTok **tidak bisa dibaca otomatis** dari environment ini (TikTok menolak request
non-browser: HTTP 403). Yang bisa dilakukan otomatis dan **sudah** dilakukan:

- semua 60 short-link di-resolve ke URL kanonik + `video_id` + handle creator (lihat
  `catalog.json` → `url`, `video_id`, `creator`).

Yang **belum** dan **harus** dilakukan oleh agen yang punya akses video (atau manusia):

- menonton/mengekstrak frame untuk mencatat timing, easing, dan teknik per video.
- mengisi field `observed` + `suggested_recipe` di `catalog.json`.

Prosedurnya ada di [`../docs/WORKFLOW-reference-to-motion.md`](../docs/WORKFLOW-reference-to-motion.md).
Sampai itu dilakukan, semua resep di `taxonomy-*.md` berstatus **inferensi struktural**
(diturunkan dari pola kategori + grammar motion graphics), bukan hasil observasi frame.

Kenapa tetap berguna? Karena resep yang dihasilkan sudah divalidasi secara mekanis
(timing, easing, overlap) dan bisa langsung dirender. Referensi dipakai sebagai
**pembanding rasa**, bukan sebagai satu-satunya sumber kebenaran.
