# 🐟 Klasifikasi Ikan Indonesia

Project machine learning end-to-end buat klasifikasi 5 jenis ikan Indonesia (**Bawal Putih, Nila, Pari, Tongkol, Tuna**) pake PyTorch, dari training sampai deployment ke web pake FastAPI + frontend.

## Struktur Project

```
PROJECT PWL/
├── dataset/                    # Data ikan (train/ + validation/)
│   ├── train/
│   │   ├── Bawal Putih/
│   │   ├── Nila/
│   │   ├── Pari/
│   │   ├── Tongkol/
│   │   └── Tuna/
│   └── validation/
│       └── ...
├── src/                        # Module ML (modular)
│   ├── config.py               # Semua hyperparameter & path
│   ├── data_loader.py          # DataLoader + augmentation + handle imbalance
│   ├── models/
│   │   ├── cnn_scratch.py      # CNN custom from scratch
│   │   └── transfer_learning.py # MobileNetV2 / ResNet18 pretrained
│   ├── train.py                # Training loop (support kedua model)
│   ├── evaluate.py             # Confusion matrix + classification report
│   └── predict.py              # Single image inference
├── app/                        # Deployment
│   ├── backend/
│   │   └── main.py             # FastAPI server
│   └── frontend/
│       ├── index.html          # UI upload + result
│       ├── style.css
│       └── script.js
├── models/                     # Saved checkpoints (auto-generated)
├── logs/                       # Training history + confusion matrix
├── notebook/
│   └── eda.ipynb
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Bikin virtual env (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt
```

## Cara Pakai

Langkah Nyalain Backend
Buka terminal baru (PowerShell / CMD), terus copy-paste ini satu per satu:
1. Masuk ke folder project
bashcd "C:\Users\User\Downloads\PROJECT PWL"
2. Install dependencies (sekali aja, kalau belum pernah)
bashpip install -r requirements.txt
Tunggu sampe selesai. Ini bakal install PyTorch, FastAPI, dll. Bisa makan waktu 2-5 menit.
3. Jalanin backend
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
Yang lo cari di output:
INFO:     Will watch for changes in these directories: ['C:\\Users\\User\\Downloads\\PROJECT PWL']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
Kalau muncul kayak gitu = aman. JANGAN TUTUP TERMINAL INI, biarin jalan.
4. Test lagi di browser
Buka http://localhost:8000 — harusnya muncul JSON.

⚠️ TAPI INGET — Predict Bakal Tetap Error Kalau Model Belum Di-train
Backend bakal jalan, tapi pas lo klik "Prediksi Sekarang" dengan model CNN from Scratch, bakal error 503 karena file models/cnn_scratch_best.pth belum ada.
Cek dulu apakah lo udah train:
bashdir "C:\Users\User\Downloads\PROJECT PWL\models"
Kalau kosong / cuma ada folder = lo belum train. Wajib train dulu sebelum bisa predict.
Cara Train (terminal terpisah lagi)
bashcd "C:\Users\User\Downloads\PROJECT PWL"

# Train transfer learning (lebih cepet, ~5-10 menit)
python -m src.train --model transfer

# Train CNN scratch (lebih lama, ~15-30 menit)
python -m src.train --model cnn_scratch

Summary Flow yang Bener
Jadi lo butuh 3 terminal kebuka bareng:
TerminalKerjaannyaCommand1Backend APIuvicorn app.backend.main:app --reload2Frontend servercd app/frontend && python -m http.server 55003Buat training (sekali doang)python -m src.train --model transfer
Coba step 1-3 dulu (nyalain backend), terus screenshot output terminal-nya. Kalau ada error pas pip 