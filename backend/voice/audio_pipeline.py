"""
AUDIO PIPELINE — full voice flow orchestrator
Voice Input → STT → Translation → AI Agents → Translation → TTS → Audio Output
"""
import tempfile, os
from voice.stt import WhisperSTT
from voice.tts import MultilingualTTS
from services.translation_service import TranslationService

class AudioPipeline:
    def __init__(self):
        self.stt         = WhisperSTT(model_size="small")
        self.tts         = MultilingualTTS()
        self.translator  = TranslationService()

    async def process_voice_query(self, audio_bytes: bytes, orchestrator, context: dict) -> dict:
        """
        Full pipeline:
        1. Save audio bytes to temp file
        2. STT → get text + detected language
        3. Translate to English for AI processing
        4. Run through multi-agent orchestrator
        5. Translate response back to farmer's language
        6. TTS → return audio bytes + text
        """
        # Step 1: Save audio
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            audio_path = tmp.name

        try:
            # Step 2: STT
            stt_result = self.stt.transcribe(audio_path)
            detected_text = stt_result["text"]
            detected_lang = stt_result["language"]

            # Step 3: Translate to English
            text_en = self.translator.to_english(detected_text, detected_lang)
            context["farmer_language"] = detected_lang

            # Step 4: AI Processing
            ai_result = await orchestrator.route(text_en, context)
            response_en = ai_result["response"]

            # Step 5: Translate back
            response_local = self.translator.from_english(response_en, detected_lang)

            # Step 6: TTS
            audio_response = self.tts.synthesize(response_local, detected_lang)

            return {
                "transcript":      detected_text,
                "detected_language": detected_lang,
                "response_text":   response_local,
                "audio_bytes":     audio_response,
                "agent_used":      ai_result.get("agent_used"),
                "agents_consulted":ai_result.get("agents_consulted", []),
            }
        finally:
            os.unlink(audio_path)
