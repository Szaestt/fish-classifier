"""
Central configuration for Indonesian Fish Classification project.
Semua hyperparameter dan path diatur di sini biar modular.
"""
from pathlib import Path

# ===== PATH CONFIG =====
ROOT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT_DIR / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "validation"
MODELS_DIR = ROOT_DIR / "models"
LOGS_DIR = ROOT_DIR / "logs"

MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ===== CLASS NAMES =====
# Diambil dari nama folder di dataset/train, sorted alfabet (default ImageFolder)
CLASS_NAMES = ["Bawal Putih", "Nila", "Pari", "Tongkol", "Tuna"]
NUM_CLASSES = len(CLASS_NAMES)

# ===== IMAGE CONFIG =====
IMG_SIZE = 224  # Standard untuk pretrained models (MobileNet, ResNet, dll)
IMG_CHANNELS = 3

# Mean & std ImageNet (dipake buat normalize transfer learning)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# ===== TRAINING CONFIG =====
BATCH_SIZE = 32
NUM_WORKERS = 2  # Set 0 di Windows kalau ada error multiprocessing
EPOCHS = 60
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 5e-4          # AdamW decoupled weight decay
EARLY_STOPPING_PATIENCE = 12

# ===== TRAINING TRICKS (v2) =====
WARMUP_EPOCHS = 3            # linear warmup sebelum cosine decay
LABEL_SMOOTHING = 0.1        # soft target, kurangi overconfidence
MIXUP_ALPHA = 0.2            # Beta(alpha, alpha) buat mixup; 0 = off
MIXUP_PROB = 0.5             # peluang batch di-mixup
GRAD_CLIP_NORM = 1.0         # gradient clipping biar stabil
RANDOM_ERASING_P = 0.25      # augmentasi: hapus patch random

# ===== DEVICE =====
import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===== MODEL CHECKPOINTS =====
CNN_SCRATCH_PATH = MODELS_DIR / "cnn_scratch_best.pth"
TRANSFER_PATH = MODELS_DIR / "transfer_best.pth"

# ===== API CONFIG =====
API_HOST = "0.0.0.0"
API_PORT = 8000

# Default model yang dipake API (bisa di-override via env)
DEFAULT_MODEL = "transfer"  # "transfer" atau "cnn_scratch"
