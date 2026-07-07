"""
Training script v2 - support kedua model (CNN scratch & Transfer Learning).

Upgrade dari v1:
- AdamW (decoupled weight decay) ganti Adam
- LR schedule: linear warmup -> cosine annealing (ganti ReduceLROnPlateau)
- Label smoothing di CrossEntropyLoss
- Mixup augmentation (probabilistik per batch)
- Gradient clipping

Usage:
    python -m src.train --model cnn_scratch
    python -m src.train --model transfer
"""
import argparse
import json
import time

import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR, LinearLR, SequentialLR
from tqdm import tqdm

from src import config
from src.data_loader import get_dataloaders
from src.models.cnn_scratch import build_cnn_scratch
from src.models.transfer_learning import build_transfer_model


def mixup_batch(images, labels, alpha: float):
    """
    Mixup: campur 2 gambar + label-nya secara linear.
    Return: mixed images, (labels_a, labels_b, lam)
    """
    lam = float(np.random.beta(alpha, alpha))
    idx = torch.randperm(images.size(0), device=images.device)
    mixed = lam * images + (1.0 - lam) * images[idx]
    return mixed, labels, labels[idx], lam


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    pbar = tqdm(loader, desc="Train", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        # Mixup (probabilistik)
        use_mixup = (
            config.MIXUP_ALPHA > 0
            and np.random.rand() < config.MIXUP_PROB
            and images.size(0) > 1
        )
        optimizer.zero_grad()
        if use_mixup:
            mixed, y_a, y_b, lam = mixup_batch(images, labels, config.MIXUP_ALPHA)
            outputs = model(mixed)
            loss = lam * criterion(outputs, y_a) + (1.0 - lam) * criterion(outputs, y_b)
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)

        loss.backward()
        # Gradient clipping biar update gak meledak (penting buat deep net + cosine LR)
        nn.utils.clip_grad_norm_(model.parameters(), config.GRAD_CLIP_NORM)
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += (preds == labels).sum().item()  # approx saat mixup, fine buat monitoring
        total += labels.size(0)
        pbar.set_postfix(loss=loss.item(), acc=correct / total)

    return running_loss / total, correct / total


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    for images, labels in tqdm(loader, desc="Val", leave=False):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    return running_loss / total, correct / total


def build_scheduler(optimizer, epochs: int):
    """Linear warmup (WARMUP_EPOCHS) lalu cosine decay sampai akhir training."""
    warmup = LinearLR(
        optimizer, start_factor=0.1, end_factor=1.0, total_iters=config.WARMUP_EPOCHS
    )
    cosine = CosineAnnealingLR(
        optimizer, T_max=max(1, epochs - config.WARMUP_EPOCHS), eta_min=1e-6
    )
    return SequentialLR(optimizer, [warmup, cosine], milestones=[config.WARMUP_EPOCHS])


def train(model_name: str, epochs: int = config.EPOCHS):
    print(f"\n{'=' * 60}")
    print(f"Training: {model_name.upper()} | Device: {config.DEVICE}")
    print(f"{'=' * 60}\n")

    # Data
    train_loader, val_loader, info = get_dataloaders(use_weighted_sampler=True)
    print(f"Train: {info['train_size']} | Val: {info['val_size']}")
    print(f"Classes: {info['idx_to_class']}\n")

    # Model
    if model_name == "cnn_scratch":
        model = build_cnn_scratch()
        save_path = config.CNN_SCRATCH_PATH
    elif model_name == "transfer":
        model = build_transfer_model(freeze_backbone=True, backbone="mobilenet_v2")
        save_path = config.TRANSFER_PATH
    else:
        raise ValueError(f"Model '{model_name}' gak dikenal. Pake 'cnn_scratch' atau 'transfer'")

    model = model.to(config.DEVICE)
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable params: {n_params:,}")

    # Loss + optimizer + scheduler
    # Label smoothing: target 1.0 -> 0.9, sisanya dibagi rata. Kurangi overfitting/overconfidence.
    criterion = nn.CrossEntropyLoss(label_smoothing=config.LABEL_SMOOTHING)
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = AdamW(trainable_params, lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY)
    scheduler = build_scheduler(optimizer, epochs)

    # Training loop
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": [], "lr": []}
    best_val_acc = 0.0
    patience_counter = 0
    start = time.time()

    for epoch in range(1, epochs + 1):
        cur_lr = optimizer.param_groups[0]["lr"]
        print(f"Epoch {epoch}/{epochs} (lr={cur_lr:.2e})")
        tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer, criterion, config.DEVICE)
        va_loss, va_acc = validate(model, val_loader, criterion, config.DEVICE)
        scheduler.step()

        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["val_loss"].append(va_loss)
        history["val_acc"].append(va_acc)
        history["lr"].append(cur_lr)

        print(f"  train_loss={tr_loss:.4f} acc={tr_acc:.4f} | val_loss={va_loss:.4f} acc={va_acc:.4f}")

        # Save best
        if va_acc > best_val_acc:
            best_val_acc = va_acc
            patience_counter = 0
            torch.save({
                "model_state": model.state_dict(),
                "model_name": model_name,
                "class_to_idx": info["class_to_idx"],
                "val_acc": va_acc,
                "epoch": epoch,
            }, save_path)
            print(f"  ✓ Saved best model (val_acc={va_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= config.EARLY_STOPPING_PATIENCE:
                print(f"  Early stopping di epoch {epoch}")
                break

    elapsed = time.time() - start
    print(f"\nTraining selesai dalam {elapsed/60:.1f} menit. Best val_acc: {best_val_acc:.4f}")

    # Save history
    history_path = config.LOGS_DIR / f"history_{model_name}.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"History saved: {history_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["cnn_scratch", "transfer"], default="transfer")
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    args = parser.parse_args()
    train(args.model, args.epochs)
