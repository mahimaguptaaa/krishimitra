'use client'
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/store/appStore'
import '@/i18n/config'
import { useTranslation } from 'react-i18next'
import api from '@/lib/api'
import MicButton from '@/components/MicButton'
import TutorialBubble from '@/components/TutorialBubble'

export default function Onboarding() {
  const router = useRouter()
  const { t } = useTranslation()
  const { token, language, setFarmerOnboarded, setFarmerCtx, newChat } = useAppStore()
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState(['', ''])
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => { if (!token) router.replace('/') }, [token])
  useEffect(() => { setTimeout(() => inputRef.current?.focus(), 200) }, [step])

  const hintKey = step === 0 ? 'hintLocation' : 'hintCrop'
  const currentHint = t(`hints.${hintKey}`)

  const handleNext = async () => {
    const val = answers[step].trim()
    if (!val) return
    if (step === 0) { setStep(1); return }
    setLoading(true)
    const location = answers[0].trim()
    const crops = answers[1].split(/[,，、\s]+/).map(c => c.trim()).filter(Boolean)
    setFarmerCtx({ location, crops, state: location })
    setFarmerOnboarded(true)
    try {
      await api.post('/api/chat', { message: `My location is ${location} and I grow ${crops.join(', ')}`, chat_id: null, language: 'en' })
    } catch {}
    newChat()
    router.push('/chat')
  }

  const handleSkip = () => { setFarmerOnboarded(true); newChat(); router.push('/chat') }
  const setAnswer = (val: string) => { const next = [...answers]; next[step] = val; setAnswers(next) }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-700 to-green-900 flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full px-6 py-8">
        <div className="flex gap-2 justify-center mb-6">
          {[0, 1].map(i => <div key={i} className={`h-2 rounded-full transition-all ${i <= step ? 'w-8 bg-green-600' : 'w-4 bg-gray-200'}`} />)}
        </div>
        <div className="text-center mb-5">
          <div className="text-4xl mb-2">{step === 0 ? '📍' : '🌱'}</div>
          <p className="text-gray-500 text-sm font-medium">{step + 1}/2</p>
        </div>

        {/* TutorialBubble's own 🔊 button already uses the fixed
            backend-first audio path -- no separate Listen button needed here */}
        <div className="flex justify-center mb-5">
          <TutorialBubble text={currentHint} language={language} />
        </div>

        <div className="flex items-center gap-2 border-2 border-gray-100 rounded-2xl px-4 py-3.5 bg-gray-50 focus-within:border-green-500 transition-colors mb-5">
          <input ref={inputRef} value={answers[step]} onChange={e => setAnswer(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleNext()}
            placeholder={step === 0 ? 'e.g. Kanpur, UP' : 'e.g. wheat, rice'}
            className="flex-1 outline-none bg-transparent text-base text-gray-900 placeholder-gray-400" />
          <MicButton language={language} onResult={txt => setAnswer(txt)} size="w-9 h-9" />
        </div>

        <button onClick={handleNext} disabled={!answers[step].trim() || loading}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-bold text-lg py-4 rounded-2xl shadow-lg active:scale-95 transition-all disabled:opacity-40">
          {loading ? '...' : step === 0 ? t('continue') + ' →' : '✓ ' + t('start')}
        </button>
        <button onClick={handleSkip} className="w-full mt-3 text-gray-400 text-sm hover:text-green-600 transition-colors">Skip →</button>
      </div>
    </div>
  )
}
