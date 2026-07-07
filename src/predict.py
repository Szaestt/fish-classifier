"""
Single-image inference module. Dipake langsung di CLI atau di-import sama API.
Usage:
    python -m src.predict --image path/to/fish.jpg --model transfer
"""
import argparse
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image

from src import config
from src.data_loader import get_transforms
from src.models.cnn_scratch import build_cnn_scratch
from src.models.transfer_learning import build_transfer_model


_MODEL_CACHE = {}  # cache biar API gak load model tiap request


def load_model(model_name: str = config.DEFAULT_MODEL):
    """Load model dari checkpoint, dengan caching."""
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]

    if model_name == "cnn_scratch":
        model = build_cnn_scratch()
        ckpt_path = config.CNN_SCRATCH_PATH
    elif model_name == "transfer":
        model = build_transfer_model()
        ckpt_path = config.TRANSFER_PATH
    else:
        raise ValueError(f"Model '{model_name}' gak dikenal")

    if not Path(ckpt_path).exists():
        raise FileNotFoundError(
            f"Checkpoint gak ada: {ckpt_path}. Train dulu dengan: python -m src.train --model {model_name}"
        )

    ckpt = torch.load(ckpt_path, map_location=config.DEVICE)
    model.load_state_dict(ckpt["model_state"])
    model = model.to(config.DEVICE)
    model.eval()

    idx_to_class = {v: k for k, v in ckpt["class_to_idx"].items()}
    _MODEL_CACHE[model_name] = (model, idx_to_class)
    return model, idx_to_class


@torch.no_grad()
def predict_image(image: Image.Image, model_name: str = config.DEFAULT_MODEL, top_k: int = 3):
    """
    Predict satu gambar.

    Args:
        image: PIL Image (RGB)
        model_name: "transfer" atau "cnn_scratch"
        top_k: berapa top prediction yang di-return

    Returns:
        dict dengan keys: prediction, confidence, top_k
    """
    model, idx_to_class = load_model(model_name)

    # Preprocess
    if image.mode != "RGB":
        image = image.convert("RGB")
    transform = get_transforms(train=False)
    tensor = transform(image).unsqueeze(0).to(config.DEVICE)

    # Inference
    logits = model(tensor)
    probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    # Top-K
    top_indices = probs.argsort()[::-1][:top_k]
    top_results = [
        {"class": idx_to_class[int(i)], "confidence": float(probs[i])}
        for i in top_indices
    ]

    best_idx = int(top_indices[0])
    return {
        "prediction": idx_to_class[best_idx],
        "confidence": float(probs[best_idx]),
        "top_k": top_results,
        "model": model_name,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path ke gambar")
    parser.add_argument("--model", choices=["cnn_scratch", "transfer"], default="transfer")
    args = parser.parse_args()

    img = Image.open(args.image)
    result = predict_image(img, model_name=args.model)
    print(f"\nPrediction: {result['prediction']} ({result['confidence']*100:.2f}%)")
    print("Top-3:")
    for r in result["top_k"]:
        print(f"  {r['class']}: {r['confidence']*100:.2f}%")
