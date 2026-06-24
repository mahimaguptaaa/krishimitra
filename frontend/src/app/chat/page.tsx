'use client'
import { useState, useRef, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import '@/i18n/config'
import i18n from '@/i18n/config'
import { useAppStore, Message } from '@/store/appStore'
import api from '@/lib/api'
import Sidebar from '@/components/Sidebar'
import { speakText, stopSpeaking, playInstructionAudio } from '@/lib/speech'
import { cleanForSpeech } from '@/lib/cleanText'

const genId = () => Math.random().toString(36).slice(2)

// FIX #5: every supported language now has its own suggested questions
// (previously only hi/en/default existed, so Punjabi/Telugu/etc. users
// saw English sample prompts).
const SUGGESTED: Record<string, string[]> = {
  hi: ['गेहूं में पीलापन क्यों है?', 'कल बारिश होगी क्या?', 'टमाटर की बीमारी देखो', 'मंडी में आज क्या भाव है?'],
  en: ['Why are wheat leaves yellow?', 'Will it rain tomorrow?', 'Identify this crop disease', 'What is the crop price today?'],
  pa: ['ਕਣਕ ਪੀਲੀ ਕਿਉਂ ਹੈ?', 'ਕੱਲ੍ਹ ਮੀਂਹ ਪਵੇਗਾ?', 'ਫਸਲ ਦੀ ਬਿਮਾਰੀ ਦੱਸੋ', 'ਅੱਜ ਮੰਡੀ ਵਿੱਚ ਭਾਅ ਕੀ ਹੈ?'],
  mr: ['गव्हाची पाने पिवळी का?', 'उद्या पाऊस येईल का?', 'या रोगाची ओळख करा', 'आज बाजारात भाव किती?'],
  bn: ['গমের পাতা হলুদ কেন?', 'কাল কি বৃষ্টি হবে?', 'এই ফসলের রোগ চিহ্নিত করুন', 'আজ বাজারে দাম কত?'],
  ta: ['கோதுமை இலைகள் ஏன் மஞ்சள்?', 'நாளை மழை பெய்யுமா?', 'இந்த பயிர் நோயை அடையாளம் காணவும்', 'இன்று சந்தை விலை என்ன?'],
  te: ['గోధుమ ఆకులు ఎందుకు పసుపు రంగులో ఉన్నాయి?', 'రేపు వర్షం పడుతుందా?', 'ఈ పంట వ్యాధిని గుర్తించండి', 'ఈరోజు మార్కెట్ ధర ఎంత?'],
  gu: ['ઘઉંના પાન પીળા કેમ છે?', 'કાલે વરસાદ થશે?', 'આ પાકના રોગને ઓળખો', 'આજે બજારમાં ભાવ શું છે?'],
  kn: ['ಗೋಧಿ ಎಲೆಗಳು ಏಕೆ ಹಳದಿ?', 'ನಾಳೆ ಮಳೆ ಬರುತ್ತದೆಯೇ?', 'ಈ ಬೆಳೆ ರೋಗ ಗುರುತಿಸಿ', 'ಇಂದು ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಏನು?'],
  ml: ['ഗോതമ്പ് ഇലകൾ മഞ്ഞയാകുന്നത് എന്തുകൊണ്ട്?', 'നാളെ മഴ പെയ്യുമോ?', 'ഈ വിള രോഗം തിരിച്ചറിയുക', 'ഇന്ന് മാർക്കറ്റ് വില എന്താണ്?'],
  default: ['What fertilizer for wheat?', 'Will it rain tomorrow?', 'Identify crop disease', "Today's market price?"],
}

function splitForSpeech(text: string, maxLen = 350): string[] {
  const clean = cleanForSpeech(text)
  const sentences = clean.split(/(?<=[.!?।])\s+/)
  const chunks: string[] = []; let cur = ''
  for (const s of sentences) {
    if ((cur + ' ' + s).length > maxLen && cur) { chunks.push(cur.trim()); cur = s }
    else cur = cur ? cur + ' ' + s : s
  }
  if (cur) chunks.push(cur.trim())
  return chunks.length ? chunks : [clean]
}

export default function ChatPage() {
  const router = useRouter()
  const { t } = useTranslation()
  const {
    token, language, theme, activeChatId, farmerCtx, tutorialDone,
    newChat, addMessage, setActiveChat, sidebarOpen,
    activeMessages, voiceSpeed, setTutorialDone,
  } = useAppStore()

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [recording, setRecording] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [speaking, setSpeaking] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const currentAudioRef = useRef<HTMLAudioElement | null>(null)
  const stopFlagRef = useRef(false)
  const messages = activeMessages()

  useEffect(() => {
    if (!token) { router.replace('/'); return }
    i18n.changeLanguage(language)
    const s = useAppStore.getState()
    if (s.sessions.length === 0) newChat()
    else if (!s.activeChatId) setActiveChat(s.sessions[0].id)
  }, [token, language])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])
  useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark') }, [theme])

  const send = useCallback(async (text: string, imgFile?: File | null) => {
    if (!text.trim() && !imgFile) return
    if (loading) return
    const chatId = activeChatId || newChat()
    setLoading(true); setInput('')
    if (textareaRef.current) textareaRef.current.style.height = '40px'

    addMessage(chatId, { id: genId(), role: 'user', content: text, imageUrl: imgFile ? URL.createObjectURL(imgFile) : undefined, timestamp: Date.now() })
    setImageFile(null); setImagePreview(null)

    try {
      let response: any
      if (imgFile) {
        const form = new FormData()
        form.append('file', imgFile)
        if (text) 
          form.append('message', text)
        form.append('language', language)
        const res = await api.post('/api/disease/predict-chat', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        response = res.data
      } else {
        const res = await api.post('/api/chat', { message: text, chat_id: chatId, language, city: farmerCtx?.location || 'Delhi' })
        response = res.data
      }
      addMessage(chatId, { id: genId(), role: 'assistant', content: response.response || response.report || 'Sorry, something went wrong.', timestamp: Date.now() })
    } catch {
      addMessage(chatId, { id: genId(), role: 'assistant', content: '⚠️ Could not reach the server. Please check your connection.', timestamp: Date.now() })
    } finally { setLoading(false) }
  }, [activeChatId, loading, language, farmerCtx])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
      chunksRef.current = []
      rec.ondataavailable = e => chunksRef.current.push(e.data)
      rec.onstop = async () => {
        setRecording(false)
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const form = new FormData()
        form.append('audio', blob, 'voice.webm')
        form.append('language', language)
        setTranscribing(true)
        try {
          const res = await api.post('/api/voice/stt', form, { headers: { 'Content-Type': 'multipart/form-data' } })
          const text = res.data.text || ''
          if (text) { setInput(text); setTimeout(() => textareaRef.current?.focus(), 50) }
        } catch {} finally { setTranscribing(false) }
      }
      recorderRef.current = rec; rec.start(); setRecording(true)
      setTimeout(() => rec.state === 'recording' && rec.stop(), 30000)
    } catch { alert(t('voiceError')) }
  }
  const stopRecording = () => { recorderRef.current?.stop(); recorderRef.current?.stream.getTracks().forEach(tr => tr.stop()) }

  const playTTS = async (msgId: string, text: string) => {
    if (speaking === msgId) {
      stopFlagRef.current = true; currentAudioRef.current?.pause(); currentAudioRef.current = null
      stopSpeaking(); setSpeaking(null); return
    }
    stopFlagRef.current = true; currentAudioRef.current?.pause(); stopSpeaking()
    await new Promise(r => setTimeout(r, 30))
    stopFlagRef.current = false; setSpeaking(msgId)
    for (const chunk of splitForSpeech(text)) {
      if (stopFlagRef.current) break
      try {
        const res = await api.post('/api/voice/tts', { text: chunk, language }, { responseType: 'blob' })
        const url = URL.createObjectURL(res.data)
        const audio = new Audio(url)
        audio.playbackRate = voiceSpeed || 1
        currentAudioRef.current = audio
        await new Promise<void>(resolve => { audio.onended = () => resolve(); audio.onerror = () => resolve(); audio.play().catch(() => resolve()) })
      } catch {
        // FIX #4: backend TTS failed for this language -- fall back to
        // browser speechSynthesis with proper voice matching instead of
        // a mispronounced offline voice.
        await speakText(chunk, language, voiceSpeed || 1)
      }
      if (stopFlagRef.current) break
    }
    currentAudioRef.current = null; setSpeaking(null)
  }

  const isDark = theme === 'dark'
  const suggestions = SUGGESTED[language] || SUGGESTED.default
  const showGuide = !tutorialDone

  return (
    <div className={`flex h-screen w-full overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      <Sidebar />

      {showGuide && (
        <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full px-6 py-7">
            <div className="text-center mb-4">
              <div className="text-4xl mb-2">🌾</div>
              <h2 className="text-lg font-bold text-gray-900">{t('hints.guideTitle')}</h2>
            </div>
            <div className="space-y-3 mb-6">
              {['guide1', 'guide2', 'guide3', 'guide4'].map(k => (
                <div key={k} className="flex items-center gap-3 bg-green-50 rounded-xl px-3 py-2.5">
                  <p className="text-sm text-gray-700 flex-1">{t(`hints.${k}`)}</p>
                  <button onClick={() => playInstructionAudio(t(`hints.${k}`), language)}
                    className="w-7 h-7 rounded-full bg-yellow-400 text-green-900 flex items-center justify-center text-xs flex-shrink-0">🔊</button>
                </div>
              ))}
            </div>
            <button onClick={() => setTutorialDone(true)}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3.5 rounded-2xl shadow-lg active:scale-95 transition-all">
              {t('hints.gotIt')}
            </button>
          </div>
        </div>
      )}

      <div className={`flex-1 flex flex-col h-screen min-w-0 transition-all ${isDark ? 'bg-gray-950' : 'bg-white'} ${sidebarOpen ? 'md:ml-64' : ''}`}>
        <header className={`flex items-center justify-between px-4 py-3 border-b sticky top-0 z-30 backdrop-blur-md
          ${isDark ? 'bg-gray-950/90 border-gray-800' : 'bg-white/90 border-gray-100'} shadow-sm`}>
          <div className={sidebarOpen ? 'w-11' : 'w-0'} />
          <div className="flex items-center gap-2">
            <span className="text-xl">🌾</span>
            <span className={`font-bold text-base ${isDark ? 'text-white' : 'text-gray-900'}`} style={{ fontFamily: "'Noto Sans Devanagari',sans-serif" }}>{t('appName')}</span>
          </div>
          <button onClick={() => newChat()} className="bg-green-600 hover:bg-green-700 text-white text-sm font-semibold px-4 py-2 rounded-xl shadow-sm transition-all active:scale-95">
            + {t('newChat')}
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="text-6xl mb-4">🌾</div>
              <h2 className={`text-xl font-bold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>{t('welcome')}</h2>
              {farmerCtx?.location && <p className="text-sm text-green-600 mb-2">📍 {farmerCtx.location}{farmerCtx.crops?.length > 0 ? ` · ${farmerCtx.crops.join(', ')}` : ''}</p>}
              <p className={`text-sm mb-6 max-w-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{t('welcomeSub')}</p>
              <div className="grid grid-cols-1 gap-2 w-full max-w-xs">
                {suggestions.map(s => (
                  <button key={s} onClick={() => send(s)}
                    className={`text-left px-4 py-3 rounded-2xl text-sm border transition-all active:scale-95
                      ${isDark ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-green-100 text-gray-700 hover:bg-green-50 bg-white shadow-sm'}`}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center text-white text-sm mr-2 flex-shrink-0 mt-1">🌾</div>}
              <div className={`max-w-[78%] rounded-2xl px-4 py-3 shadow-sm
                ${msg.role === 'user' ? 'bg-green-600 text-white rounded-tr-sm' : isDark ? 'bg-gray-800 text-gray-100 rounded-tl-sm' : 'bg-gray-100 text-gray-900 rounded-tl-sm'}`}>
                {msg.imageUrl && <img src={msg.imageUrl} alt="" className="w-48 h-36 object-cover rounded-xl mb-2" />}
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                {msg.role === 'assistant' && (
                  <button onClick={() => playTTS(msg.id, msg.content)}
                    className={`mt-2 flex items-center gap-1 text-xs opacity-60 hover:opacity-100 transition-opacity ${speaking === msg.id ? 'text-green-500' : ''}`}>
                    {speaking === msg.id ? '⏹ ' + t('stop') : '🔊 ' + t('listen')}
                  </button>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center text-white text-sm mr-2">🌾</div>
              <div className={`rounded-2xl rounded-tl-sm px-4 py-3 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
                <div className="flex gap-1 items-center h-5">{[0, 1, 2].map(i => <div key={i} className="w-2 h-2 rounded-full bg-green-500 typing-dot" />)}</div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {imagePreview && (
          <div className={`px-4 py-2 border-t flex items-center gap-3 ${isDark ? 'border-gray-800 bg-gray-900' : 'border-gray-100 bg-gray-50'}`}>
            <img src={imagePreview} alt="" className="w-14 h-14 object-cover rounded-xl" />
            <p className={`text-sm flex-1 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>📷 Photo ready</p>
            <button onClick={() => { setImageFile(null); setImagePreview(null) }} className="text-red-400 text-lg font-bold">✕</button>
          </div>
        )}

        <div className={`px-4 pb-6 pt-3 border-t ${isDark ? 'border-gray-800 bg-gray-950' : 'border-gray-100 bg-white'}`}>
          <div className="flex items-center gap-2 max-w-3xl mx-auto">
            <button onClick={() => fileRef.current?.click()} className="w-11 h-11 rounded-full bg-yellow-400 hover:bg-yellow-500 text-green-900 flex items-center justify-center flex-shrink-0 shadow-sm transition-all" title={t('attach')}>🖼️</button>
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={e => e.target.files?.[0] && (setImageFile(e.target.files[0]), setImagePreview(URL.createObjectURL(e.target.files[0])))} />

            <button onClick={recording ? stopRecording : startRecording} disabled={loading && !recording}
              className={`w-11 h-11 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm transition-all ${recording ? 'bg-red-500 text-white animate-pulse' : 'bg-yellow-400 hover:bg-yellow-500 text-green-900'}`}>
              {transcribing ? '⏳' : '🎤'}
            </button>

            <div className={`flex-1 flex items-center rounded-full border-2 px-4 py-1 ${isDark ? 'border-gray-700 bg-gray-900 focus-within:border-green-500' : 'border-gray-200 bg-gray-50 focus-within:border-green-400 shadow-sm'}`}>
              <textarea ref={textareaRef} value={input}
                onChange={e => { setInput(e.target.value); e.target.style.height = 'auto'; e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px' }}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input, imageFile) } }}
                placeholder={transcribing ? t('listening') : t('placeholder')} rows={1} disabled={loading}
                className={`flex-1 bg-transparent outline-none resize-none text-sm leading-relaxed py-2 ${isDark ? 'text-white placeholder-gray-500' : 'text-gray-800 placeholder-gray-400'}`}
                style={{ minHeight: '40px', maxHeight: '100px' }} />
            </div>

            <button onClick={() => send(input, imageFile)} disabled={loading || (!input.trim() && !imageFile)}
              className="w-11 h-11 rounded-full bg-green-600 text-white flex items-center justify-center flex-shrink-0 hover:bg-green-700 active:scale-90 transition-all disabled:opacity-40 shadow-md">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
          {recording && <p className="text-center text-red-500 text-xs mt-2 animate-pulse">🔴 {t('listening')}</p>}
          {transcribing && <p className="text-center text-green-500 text-xs mt-2">✍️ Converting speech to text...</p>}
        </div>
      </div>
    </div>
  )
}
