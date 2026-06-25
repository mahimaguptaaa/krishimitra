import json
from pathlib import Path

LABELS_PATH  = Path(__file__).parent / "labels.json"
WEIGHTS_PATH = Path(__file__).parent / "weights" / "model.pt"

class DiseaseModel:
    NUM_CLASSES = 38

    def __init__(self):
        # Lazy imports - torch only loads when DiseaseModel is first used
        import torch
        import torchvision.transforms as T
        import torchvision.models as models
        self._torch = torch

        self.labels = json.loads(LABELS_PATH.read_text())
        self.model  = self._load_model()
        self.transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _load_model(self):
        import torchvision.models as models
        if not WEIGHTS_PATH.exists():
            raise FileNotFoundError(
                f"Model weights not found at {WEIGHTS_PATH}. "
                "Run: python scripts/download_model.py"
            )
        m = models.efficientnet_b0(weights=None)
        m.classifier[1] = self._torch.nn.Linear(1280, self.NUM_CLASSES)
        m.load_state_dict(self._torch.load(str(WEIGHTS_PATH), map_location="cpu"))
        m.eval()
        return m

    def predict(self, image_path: str) -> dict:
        from PIL import Image
        img    = Image.open(image_path).convert("RGB")
        tensor = self.transform(img).unsqueeze(0)
        with self._torch.no_grad():
            probs = self._torch.softmax(self.model(tensor), dim=1)[0]
        top3_probs, top3_idx = self._torch.topk(probs, 3)
        top_k = [
            {"label": self.labels[i.item()], "confidence": round(p.item(), 4)}
            for p, i in zip(top3_probs, top3_idx)
        ]
        top_confidence = top_k[0]["confidence"]
        if top_confidence < 0.50:
            return {
                "label": None,
                "confidence": top_confidence,
                "top_k": top_k,
                "not_a_crop": True,
            }
        return {
            "label": top_k[0]["label"],
            "confidence": top_k[0]["confidence"],
            "top_k": top_k,
        }