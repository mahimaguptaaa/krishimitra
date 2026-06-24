from agents.base_agent import BaseAgent
from services.llm_service import LLMService

REPORT_PROMPT = """
A farmer's crop has been diagnosed with: {disease}
Confidence: {confidence}%

Write a clear, farmer-friendly disease report with these sections:

1. What is this disease?
2. Symptoms to look for
3. What causes it
4. Organic treatment (practical, affordable)
5. Chemical treatment (name, dosage, safety warning)
6. How to prevent it in future
7. Urgency: LOW / MEDIUM / HIGH (and why)

Use simple language. Farmer may have limited education.
Keep total response under 400 words.
"""

NOT_A_CROP_RESPONSE = (
    "यह छवि किसी कृषि फसल की नहीं लगती। "
    "कृपया अपनी फसल (जैसे गेहूं, टमाटर, आलू आदि) की पत्ती या पौधे की "
    "स्पष्ट फोटो अपलोड करें। 🌱"
)


class DiseaseAgent(BaseAgent):
    def __init__(self):
        self.llm = LLMService()

    async def run(self, query: str, context: dict) -> dict:
        image_path = context.get("image_path")

        if not image_path:
            return {
                "response": "Please upload a photo of your crop so I can diagnose the disease.",
                "sources": []
            }

        # ── Step 1: Vision check — is this an agricultural crop? ─────────────
        is_crop = self.llm.is_crop_image(image_path)
        if not is_crop:
            return {
                "response": NOT_A_CROP_RESPONSE,
                "sources": [],
                "metadata": {
                    "disease_name": None,
                    "confidence": 0,
                    "top_k": [],
                    "not_a_crop": True,
                }
            }
        # ─────────────────────────────────────────────────────────────────────

        # ── Step 2: Run disease model ─────────────────────────────────────────
        try:
            from ml.disease_model import DiseaseModel
            model = DiseaseModel()
            prediction = model.predict(image_path)
        except FileNotFoundError:
            return {
                "response": (
                    "Disease model weights not found. "
                    "Please download the model weights first (see README)."
                ),
                "sources": []
            }

        # ── Step 3: Confidence threshold check ───────────────────────────────
        if prediction.get("not_a_crop"):
            return {
                "response": NOT_A_CROP_RESPONSE,
                "sources": [],
                "metadata": {
                    "disease_name": None,
                    "confidence": prediction["confidence"],
                    "top_k": prediction["top_k"],
                    "not_a_crop": True,
                }
            }
        # ─────────────────────────────────────────────────────────────────────

        disease = prediction["label"]
        confidence = round(prediction["confidence"] * 100, 1)
        report = self.llm.complete(
            REPORT_PROMPT.format(disease=disease, confidence=confidence)
        )

        return {
            "response": report,
            "sources": ["PlantVillage Disease Model"],
            "metadata": {
                "disease_name": disease,
                "confidence": prediction["confidence"],
                "top_k": prediction["top_k"],
                "not_a_crop": False,
            }
        }