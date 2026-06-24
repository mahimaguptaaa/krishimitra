from config import settings

# Short domain-relevant phrases per language help Whisper's decoder bias
# toward farming vocabulary and correct sentence structure, improving
# accuracy on short utterances (names, places, crop names).
INITIAL_PROMPTS = {
    "hi": "किसान गेहूं चावल बारिश मौसम खाद फसल कीट गांव जिला",
    "en": "farmer wheat rice rain weather fertilizer crop pest village district",
    "pa": "ਕਿਸਾਨ ਕਣਕ ਚੌਲ ਮੀਂਹ ਮੌਸਮ ਖਾਦ ਫ਼ਸਲ",
    "mr": "शेतकरी गहू भात पाऊस हवामान खत पीक",
    "bn": "কৃষক গম ধান বৃষ্টি আবহাওয়া সার ফসল",
    "ta": "விவசாயி கோதுமை அரிசி மழை வானிலை உரம் பயிர்",
    "te": "రైతు గోధుమ వరి వర్షం వాతావరణం ఎరువు పంట",
    "gu": "ખેડૂત ઘઉં ડાંગર વરસાદ હવામાન ખાતર પાક",
    "kn": "ರೈತ ಗೋಧಿ ಭತ್ತ ಮಳೆ ಹವಾಮಾನ ಗೊಬ್ಬರ ಬೆಳೆ",
    "ml": "കർഷകൻ ഗോതമ്പ് നെല്ല് മഴ കാലാവസ്ഥ വളം വിള",
}

class WhisperSTT:
    _model = None

    def __init__(self, model_size: str = None):
        if WhisperSTT._model is None:
            from faster_whisper import WhisperModel
            size = model_size or settings.WHISPER_MODEL_SIZE
            WhisperSTT._model = WhisperModel(size, device="cpu", compute_type="int8")
        self.model = WhisperSTT._model

    def transcribe(self, audio_path: str, language: str = None) -> dict:
        lang = language or "hi"
        prompt = INITIAL_PROMPTS.get(lang, INITIAL_PROMPTS["hi"])

        # FIX #1: tuned for short, noisy farmer audio clips --
        # higher beam_size + best_of improve accuracy, temperature=0
        # makes output deterministic (no random rambling), tighter VAD
        # silence threshold avoids trimming the start/end of short words,
        # and initial_prompt biases the decoder toward farming vocabulary
        # for more correct sentence structure.
        segments, info = self.model.transcribe(
            audio_path,
            language=lang,
            beam_size=8,
            best_of=5,
            temperature=0,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 300},
            condition_on_previous_text=False,
            initial_prompt=prompt,
        )
        text = " ".join(seg.text for seg in segments).strip()
        return {
            "text": text,
            "language": info.language,
            "confidence": round(info.language_probability, 2),
        }

SUPPORTED = {"hi": "Hindi", "en": "English", "mr": "Marathi", "pa": "Punjabi", "bn": "Bengali",
             "ta": "Tamil", "te": "Telugu", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam"}
