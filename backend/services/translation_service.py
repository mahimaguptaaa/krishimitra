"""
ADVANCED MULTILINGUAL SERVICE
Primary: deep-translator (free, no key needed, 100+ languages)
Upgrade path: IndicTrans2 (fully local, best Indian language quality)

Supports: Hindi, English, Marathi, Punjabi, Bengali, Tamil, Telugu,
          Gujarati, Kannada, Malayalam + any Google Translate language
"""
from langdetect import detect

# Language metadata for UI
SUPPORTED_LANGUAGES = {
    "hi": {"name": "हिंदी",    "english": "Hindi",     "flag": "🇮🇳"},
    "en": {"name": "English",   "english": "English",   "flag": "🇬🇧"},
    "mr": {"name": "मराठी",    "english": "Marathi",   "flag": "🇮🇳"},
    "pa": {"name": "ਪੰਜਾਬੀ",   "english": "Punjabi",   "flag": "🇮🇳"},
    "bn": {"name": "বাংলা",     "english": "Bengali",   "flag": "🇮🇳"},
    "ta": {"name": "தமிழ்",    "english": "Tamil",     "flag": "🇮🇳"},
    "te": {"name": "తెలుగు",   "english": "Telugu",    "flag": "🇮🇳"},
    "gu": {"name": "ગુજરાતી",  "english": "Gujarati",  "flag": "🇮🇳"},
    "kn": {"name": "ಕನ್ನಡ",   "english": "Kannada",   "flag": "🇮🇳"},
    "ml": {"name": "മലയാളം",   "english": "Malayalam", "flag": "🇮🇳"},
    "bh": {"name": "भोजपुरी",  "english": "Bhojpuri",  "flag": "🇮🇳"},  # via Hindi
}

# Bhojpuri maps to Hindi for translation (closest available)
_LANG_REMAP = {"bh": "hi"}

class TranslationService:
    def __init__(self):
        try:
            from deep_translator import GoogleTranslator
            self._translator_cls = GoogleTranslator
            self._backend = "deep_translator"
        except ImportError:
            self._backend = "none"

    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            return lang if lang in SUPPORTED_LANGUAGES else "en"
        except Exception:
            return "en"

    def to_english(self, text: str, source_lang: str) -> str:
        if source_lang == "en" or not text.strip():
            return text
        src = _LANG_REMAP.get(source_lang, source_lang)
        return self._translate(text, src, "en")

    def from_english(self, text: str, target_lang: str) -> str:
        if target_lang == "en" or not text.strip():
            return text
        tgt = _LANG_REMAP.get(target_lang, target_lang)
        return self._translate(text, "en", tgt)

    def translate(self, text: str, source: str, target: str) -> str:
        src = _LANG_REMAP.get(source, source)
        tgt = _LANG_REMAP.get(target, target)
        return self._translate(text, src, tgt)

    def _translate(self, text: str, source: str, target: str) -> str:
        if source == target:
            return text
        if self._backend == "deep_translator":
            try:
                from deep_translator import GoogleTranslator
                # Split long text into chunks (Google limit ~5000 chars)
                if len(text) > 4500:
                    chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                    translated = [GoogleTranslator(source=source, target=target).translate(c) for c in chunks]
                    return " ".join(translated)
                return GoogleTranslator(source=source, target=target).translate(text)
            except Exception as e:
                return text  # fallback: return original
        return text

    @staticmethod
    def supported_languages() -> dict:
        return SUPPORTED_LANGUAGES
