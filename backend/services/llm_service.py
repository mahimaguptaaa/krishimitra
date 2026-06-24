"""
LLM SERVICE WITH FALLBACK CHAIN
Tier 1: Gemini 2.5 Flash (primary)
Tier 2: Groq API (free tier, very fast)
Tier 3: Ollama local (llama3.1:8b or qwen3:8b)
"""
import httpx
from config import settings

class LLMService:
    def complete(self, prompt: str, max_tokens: int = 1024) -> str:
        if settings.GEMINI_API_KEY:
            try:
                return self._gemini(prompt)
            except Exception as e:
                print(f"[LLM] Gemini failed: {e}, trying Groq...")

        if settings.GROQ_API_KEY:
            try:
                return self._groq(prompt, max_tokens)
            except Exception as e:
                print(f"[LLM] Groq failed: {e}, trying Ollama...")

        try:
            return self._ollama(prompt, max_tokens)
        except Exception as e:
            print(f"[LLM] Ollama failed: {e}")
            return "Sorry, all AI services are temporarily unavailable. Please try again in a moment."

    def is_crop_image(self, image_path: str) -> bool:
        """
        Checks if image contains an AGRICULTURAL CROP (not flowers, scenery, food, people).
        Tries Groq vision first (to save Gemini quota), then Gemini, then allows through.
        """
        # Try Groq vision first (free, saves Gemini quota)
        if settings.GROQ_API_KEY:
            try:
                result = self._groq_vision_check(image_path)
                print(f"[LLM] Groq crop check: {result}")
                return result
            except Exception as e:
                print(f"[LLM] Groq vision failed: {e}, trying Gemini...")

        # Fallback to Gemini vision
        if settings.GEMINI_API_KEY:
            try:
                result = self._gemini_vision_check(image_path)
                print(f"[LLM] Gemini crop check: {result}")
                return result
            except Exception as e:
                print(f"[LLM] Gemini vision failed: {e}, allowing through")

        # If both fail, allow through (don't block valid images)
        return True

    def _groq_vision_check(self, image_path: str) -> bool:
        """Use Groq llama-3.2-11b-vision to check if image is an agricultural crop."""
        import base64

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Detect image type from extension
        ext = image_path.lower().split(".")[-1]
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.2-11b-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Is this image showing a crop plant or leaf that a farmer grows "
                                    "for agriculture such as wheat, rice, tomato, corn, potato, "
                                    "cotton, sugarcane, or any vegetable/fruit crop? "
                                    "Flowers, scenery, mountains, people, food dishes, and "
                                    "ornamental plants do NOT count. "
                                    "Reply with only YES or NO. Nothing else."
                                )
                            }
                        ]
                    }
                ],
                "max_tokens": 5,
            },
            timeout=30
        )
        answer = resp.json()["choices"][0]["message"]["content"].strip().upper()
        return answer.startswith("YES")

    def _gemini_vision_check(self, image_path: str) -> bool:
        """Use Gemini Vision to check if image is an agricultural crop."""
        import google.generativeai as genai
        from PIL import Image

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        img = Image.open(image_path)
        response = model.generate_content([
            img,
            (
                "Is this image showing a crop plant or leaf that a farmer grows "
                "for agriculture such as wheat, rice, tomato, corn, potato, "
                "cotton, sugarcane, or any vegetable/fruit crop? "
                "Flowers, scenery, mountains, people, food dishes, and "
                "ornamental plants do NOT count. "
                "Reply with only YES or NO. Nothing else."
            )
        ])
        answer = response.text.strip().upper()
        return answer.startswith("YES")

    def _gemini(self, prompt: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model.generate_content(prompt).text

    def _groq(self, prompt: str, max_tokens: int) -> str:
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            },
            timeout=30
        )
        return resp.json()["choices"][0]["message"]["content"]

    def _ollama(self, prompt: str, max_tokens: int) -> str:
        resp = httpx.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens}
            },
            timeout=120
        )
        return resp.json()["response"]