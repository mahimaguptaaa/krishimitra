"""
RICH DISEASE PIPELINE
Returns structured analysis: disease, severity, affected region,
organic remedy, chemical remedy, prevention.
"""
from services.llm_service import LLMService
import json, re

RICH_REPORT_PROMPT = """
A crop disease has been detected: {disease}
Confidence: {confidence}%

Return a JSON object with EXACTLY these keys:
{{
  "disease": "{disease}",
  "confidence": {confidence},
  "severity": "Low|Medium|High|Critical",
  "affected_region": "which part of plant is affected",
  "spread_risk": "Low|Medium|High",
  "organic_remedy": "practical organic treatment steps",
  "chemical_remedy": "chemical treatment with dosage and safety note",
  "prevention": "how to prevent recurrence",
  "urgency": "Act within 24hrs|Act within 3 days|Monitor weekly",
  "government_support": "any PM scheme or KVK support available"
}}

Return ONLY valid JSON. No explanation outside JSON.
"""

class DiseasePipeline:
    def __init__(self):
        self.llm = LLMService()

    def classify(self, image_path: str) -> dict:
        """Run EfficientNet model."""
        from ml.disease_model import DiseaseModel
        model = DiseaseModel()
        return model.predict(image_path)

    def analyze(self, image_path: str) -> dict:
        """Full pipeline: classify + generate rich structured report."""
        pred = self.classify(image_path)
        disease  = pred["label"]
        confidence = round(pred["confidence"] * 100, 1)

        raw = self.llm.complete(RICH_REPORT_PROMPT.format(
            disease=disease, confidence=confidence
        ))

        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            structured = json.loads(match.group()) if match else {}
        except Exception:
            structured = {}

        # Fallback defaults
        structured.setdefault("disease", disease)
        structured.setdefault("confidence", confidence)
        structured.setdefault("severity", "Unknown")
        structured.setdefault("organic_remedy", "Consult local KVK officer.")
        structured.setdefault("chemical_remedy", "Consult agrochemist.")
        structured.setdefault("prevention", "Maintain crop hygiene.")
        structured.setdefault("urgency", "Monitor weekly")

        structured["top_k"] = pred.get("top_k", [])
        return structured
