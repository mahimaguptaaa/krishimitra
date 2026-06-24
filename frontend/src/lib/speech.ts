import { cleanForSpeech } from './cleanText'
import api from './api'

const VOICE_LANG_MAP: Record<string, string> = {
  hi: 'hi-IN', en: 'en-IN', pa: 'pa-IN', mr: 'mr-IN', bn: 'bn-IN',
  ta: 'ta-IN', te: 'te-IN', gu: 'gu-IN', kn: 'kn-IN', ml: 'ml-IN',
}

let cachedVoices: SpeechSynthesisVoice[] = []

function loadVoices(): Promise<SpeechSynthesisVoice[]> {
  return new Promise(resolve => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) { resolve([]); return }
    const v = window.speechSynthesis.getVoices()
    if (v.length) { cachedVoices = v; resolve(v); return }
    window.speechSynthesis.onvoiceschanged = () => {
      cachedVoices = window.speechSynthesis.getVoices()
      resolve(cachedVoices)
    }
    setTimeout(() => resolve(window.speechSynthesis.getVoices()), 500)
  })
}

// Browser-only TTS (last-resort fallback). Quality depends entirely on
// which voices are installed on the user's device/OS -- most Windows/
// Android setups only ship English (and sometimes Hindi) voices, so
// other languages can sound wrong or be silently substituted.
export async function speakText(text: string, langCode: string, rate = 1): Promise<void> {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text?.trim()) return
  const clean = cleanForSpeech(text)
  window.speechSynthesis.cancel()
  const bcp47 = VOICE_LANG_MAP[langCode] || 'hi-IN'
  const voices = cachedVoices.length ? cachedVoices : await loadVoices()
  const voice =
    voices.find(v => v.lang === bcp47) ||
    voices.find(v => v.lang?.toLowerCase().startsWith(langCode)) ||
    null

  return new Promise(resolve => {
    const utt = new SpeechSynthesisUtterance(clean)
    utt.lang = bcp47
    if (voice) utt.voice = voice
    utt.rate = rate
    utt.onend = () => resolve()
    utt.onerror = () => resolve()
    window.speechSynthesis.speak(utt)
  })
}

// FIX: instruction bubbles (Login/Onboarding/chat guide/Settings preview)
// were calling speakText() directly, which ONLY uses the browser's local
// voices -- producing gibberish for languages with no installed voice.
// This function tries the backend's gTTS-based /api/voice/tts FIRST
// (same engine the chat replies already use correctly), and only falls
// back to the browser voice if the backend is unreachable.
export async function playInstructionAudio(text: string, langCode: string, rate = 1): Promise<void> {
  const clean = cleanForSpeech(text)
  if (!clean.trim()) return
  try {
    const res = await api.post('/api/voice/tts', { text: clean, language: langCode }, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const audio = new Audio(url)
    audio.playbackRate = rate
    await new Promise<void>(resolve => {
      audio.onended = () => resolve()
      audio.onerror = () => resolve()
      audio.play().catch(() => resolve())
    })
  } catch {
    await speakText(clean, langCode, rate)
  }
}

export function stopSpeaking() {
  if (typeof window !== 'undefined') window.speechSynthesis?.cancel()
}
