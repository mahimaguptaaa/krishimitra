import os, tempfile
from pathlib import Path
from utils.text_clean import clean_for_speech

class MultilingualTTS:
    LANG_MAP = {
        "hi": "hi", "en": "en", "mr": "mr", "pa": "hi", "bn": "bn",
        "ta": "ta", "te": "te", "gu": "gu", "kn": "kn", "ml": "ml", "bh": "hi",
    }

    def synthesize(self, text: str, language: str = "hi") -> bytes:
        # FIX #8: strip markdown symbols ("-", "*", "#" etc.) before speaking
        clean_text = clean_for_speech(text)
        if not clean_text.strip():
            clean_text = text

        gtts_lang = self.LANG_MAP.get(language, "hi")
        try:
            return self._gtts(clean_text, gtts_lang)
        except Exception:
            # FIX #4: previously this silently fell back to pyttsx3, which
            # reads native-script text (Telugu/Gujarati/etc.) using an
            # English-only system voice -- producing the "gibberish"
            # pronunciation reported. We now raise instead, so the
            # frontend's browser-based fallback (which picks a real
            # matching voice for the language) is used instead of a
            # mispronounced offline voice.
            raise

    def _gtts(self, text: str, lang: str) -> bytes:
        from gtts import gTTS
        import io
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()

    def synthesize_to_file(self, text: str, language: str = "hi", output_dir: str = "uploads/audio") -> str:
        import uuid
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        audio_bytes = self.synthesize(text, language)
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        return filepath
