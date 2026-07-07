# 🐟 Klasifikasi Ikan Indonesia — Versi PHP

Klasifikasi 5 jenis ikan (**Bawal Putih, Nila, Pari, Tongkol, Tuna**) dengan **inference CNN 100% PHP murni**. Tanpa Python, tanpa PyTorch, tanpa server ML eksternal saat runtime. Tinggal upload gambar → dapat prediksi + top-3 confidence.

> Versi ini hasil konversi dari project PyTorch + FastAPI. Bobot model CNN (yang sudah di-train, val_acc ~83%) diekspor ke format biner, lalu forward-pass-nya direimplement penuh di PHP. Output-nya **cocok persis** dengan versi PyTorch (selisih numerik ~2e-7).

## Struktur

```
fish-classifier-php/
├── public/                 # Web root (docroot Apache/PHP ke sini)
│   ├── index.php           # UI: drag & drop upload + hasil
│   ├── predict.php         # API: POST gambar -> JSON prediksi
│   ├── classes.php         # API: info model & daftar kelas
│   └── assets/             # style.css + app.js
├── src/                    # Engine inference (pengganti src/ Python)
│   ├── WeightLoader.php    # baca bobot .bin + manifest .json
│   ├── Preprocess.php      # GD: resize 224 + normalize ImageNet
│   ├── FishCNN.php         # forward pass: conv/bn(fold)/relu/maxpool/gap/linear
│   └── Classifier.php      # gabungan jadi 1 API high-level
├── weights/
│   ├── cnn_scratch.json    # manifest (shape + offset tiap param + kelas)
│   └── cnn_scratch.bin     # bobot float32 (~1.6 MB)
├── cli.php                 # inference lewat terminal
├── config.php             # konfigurasi (resolusi, top_k, dll)
├── Dockerfile             # buat deploy online
├── docker-entrypoint.sh
└── tools/export_weights.py # OPSIONAL: regenerasi bobot dari .pth (butuh Python sekali)
```

## Jalanin di Lokal

Butuh PHP 8.x dengan ekstensi **GD** (cek: `php -m | grep gd`).

```bash
cd fish-classifier-php
php -S localhost:8000 -t public
```

Buka **http://localhost:8000** → upload gambar ikan → klik **Prediksi Sekarang**.

Lewat terminal:
```bash
php cli.php path/ke/ikan.jpg
```

## Deploy Online (beneran, gratis)

Engine ini jalan di mana aja yang support PHP + GD. Karena inference agak berat (beberapa detik), **pakai Docker host** yang bebas atur timeout — paling gampang **Render.com**.

### Opsi A — Render.com (rekomendasi, ada free tier)
1. Push folder ini ke repo GitHub.
2. render.com → **New → Web Service** → connect repo.
3. Render auto-detect `Dockerfile`. Environment: **Docker**. Klik **Create**.
4. Tunggu build selesai → dapat URL publik `https://namamu.onrender.com`. Selesai.

> Dockerfile sudah handle `$PORT` dari Render otomatis lewat `docker-entrypoint.sh`.

### Opsi B — Railway.app
1. Push ke GitHub → railway.app → **New Project → Deploy from GitHub**.
2. Railway baca `Dockerfile` otomatis → **Generate Domain** buat dapat URL publik.

### Opsi C — VPS (DigitalOcean/dll) atau shared hosting
- VPS: `docker build -t fish . && docker run -p 80:80 fish`.
- Shared hosting (cPanel): upload semua file, set **document root** ke folder `public/`. Pastikan PHP 8 + GD aktif, dan `max_execution_time` ≥ 60 (file `.htaccess` sudah nyetel ini).

> ⚠️ Hindari free host yang maksa `max_execution_time` ≤ 10s (mis. InfinityFree) — inference bisa ke-cut. Pakai resolusi 128px (lebih cepat) atau host Docker.

## Pakai API

```bash
# prediksi
curl -X POST -F "file=@ikan.jpg" https://URL-KAMU/predict.php

# info model
curl https://URL-KAMU/classes.php
```

Contoh respons `predict.php`:
```json
{
  "prediction": "Nila",
  "confidence": 0.999,
  "top_k": [
    {"class": "Nila", "confidence": 0.999},
    {"class": "Tongkol", "confidence": 0.0009},
    {"class": "Bawal Putih", "confidence": 0.00002}
  ],
  "model": "cnn_scratch",
  "input_size": 160,
  "elapsed_ms": 8100
}
```

## Catatan Teknis

- **Kenapa CNN scratch, bukan MobileNetV2?** Arsitektur transfer learning (50+ layer) terlalu berat & rawan bug kalau direimplement di PHP murni. CNN scratch cuma 4 conv block — bersih, akurat, dan outputnya bisa diverifikasi 1:1 dengan PyTorch.
- **BatchNorm di-fold ke conv** saat load (math BN bersifat affine di inference), jadi hemat satu pass.
- **Conv pakai tap-based accumulation** + input padding → jauh lebih cepat dari nested-loop naif (100s+ → belasan detik di 224px).
- **Resolusi bisa diatur** di `config.php` (`img_size`). Model pakai Global Average Pooling jadi fleksibel:

  | img_size | kecepatan | akurasi |
  |----------|-----------|---------|
  | 224      | ~14 s     | paling akurat (identik PyTorch) |
  | 160 (default) | ~7 s | sangat baik |
  | 128      | ~5 s      | baik (uji 5/5 benar) |

## Regenerasi Bobot (opsional)

Bobot di `weights/` sudah jadi — **tidak perlu Python buat menjalankan app**. Kalau suatu saat kamu re-train model PyTorch dan mau update bobotnya, jalankan sekali:
```bash
python tools/export_weights.py   # baca models/cnn_scratch_best.pth -> weights/*.bin + .json
```
Ini satu-satunya tempat Python dipakai, dan murni langkah build offline — bukan bagian dari runtime.
