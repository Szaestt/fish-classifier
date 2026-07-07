"""
Transfer learning model - pake MobileNetV2 (ringan, cepat, akurat) dari ImageNet.
Default: freeze backbone, train classifier head only. Bisa di-unfreeze buat fine-tuning.
"""
import torch
import torch.nn as nn
from torchvision import models
from src import config

def build_transfer_model(
    num_classes: int = config.NUM_CLASSES,
    freeze_backbone: bool = True,
    backbone: str = "mobilenet_v2",
) -> nn.Module:
    """
    Build pretrained model dengan custom classifier head.

    Args:
        num_classes: jumlah kelas output
        freeze_backbone: True = transfer learning (freeze), False = fine-tuning
        backbone: "mobilenet_v2" atau "resnet18"

    Returns:
        nn.Module yang siap di-train
    """
    if backbone == "mobilenet_v2":
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        if freeze_backbone:
            for param in model.features.parameters():
                param.requires_grad = False
        # Replace classifier head
        in_features = model.classifier[-1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        )

    elif backbone == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        )

    else:
        raise ValueError(f"Backbone '{backbone}' belum di-support. Pake 'mobilenet_v2' atau 'resnet18'")

    return model


def unfreeze_backbone(model: nn.Module):
    """
    Buat fine-tuning stage. Unfreeze semua params, biasanya pake LR lebih kecil.
    """
    for param in model.parameters():
        param.requires_grad = True
    return model


if __name__ == "__main__":
    model = build_transfer_model()
    x = torch.randn(2, 3, 224, 224)
    out = model(x)
    print(f"Output shape: {out.shape}")
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    print(f"Trainable: {n_trainable:,} / Total: {n_total:,}")
