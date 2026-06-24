'use client'
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/store/appStore'
import '@/i18n/config'
import { useTranslation } from 'react-i18next'
import api from '@/lib/api'
import MicButton from '@/components/MicButton'
import TutorialBubble from '@/components/TutorialBubble'

export default function Login() {
  const router = useRouter()
  const { setToken, setPhone, setUserName, language } = useAppStore()
  const { t } = useTranslation()
  const [step, setStep] = useState<'details' | 'otp'>('details')
  const [name, setName] = useState('')
  const [phone, setPhoneVal] = useState('')
  const [otp, setOtp] = useState(['', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [countdown, setCountdown] = useState(0)
  const [notif, setNotif] = useState<string | null>(null)
  const refs = [useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null)]

  useEffect(() => {
    if (countdown > 0) { const tm = setTimeout(() => setCountdown(c => c - 1), 1000); return () => clearTimeout(tm) }
  }, [countdown])

  const currentHint =
    step === 'otp' ? t('hints.hintOtp')
    : !name.trim() ? t('hints.hintName')
    : t('hints.hintPhone')

  const showSms = (code: string) => {
    setNotif(`📩 OTP: ${code}`)
    setTimeout(() => setNotif(null), 7000)
  }

  const sendOtp = async () => {
    if (!name.trim()) { setError(t('enterName')); return }
    if (phone.replace(/\D/g, '').length < 10) { setError('Please enter a valid 10-digit phone number'); return }
    setLoading(true); setError('')
    try {
      const res = await api.post('/api/auth/send-otp', { phone: phone.replace(/\D/g, ''), name: name.trim() })
      showSms(res.data.debug_otp || '')
      setOtp(['', '', '', ''])
      setStep('otp'); setCountdown(30)
      setTimeout(() => refs[0].current?.focus(), 200)
    } catch {
      setError('Could not send OTP. Please check your connection and try again.')
    } finally { setLoading(false) }
  }

  const handleOtpChange = (i: number, val: string) => {
    if (!/^[0-9]?$/.test(val)) return
    const next = [...otp]; next[i] = val; setOtp(next)
    if (val && i < 3) refs[i + 1].current?.focus()
  }

  // FIX #2: real OTP validation. Wrong codes now show an error and do
  // NOT log the user in (previously any failure silently let them through
  // with a fake demo token).
  const verifyOtp = async () => {
    const code = otp.join('')
    if (code.length < 4) { setError('Enter the 4-digit OTP'); return }
    setLoading(true); setError('')
    try {
      const res = await api.post('/api/auth/verify-otp', { phone: phone.replace(/\D/g, ''), otp: code })
      const token = res.data.access_token
      localStorage.setItem('km_token', token)
      setToken(token); setPhone(phone); setUserName(res.data.user?.name || name || 'Farmer')
      router.push('/onboarding')
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Incorrect OTP. Please try again.'
      setError(msg)
      setOtp(['', '', '', ''])
      refs[0].current?.focus()
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-700 to-green-900 flex items-center justify-center px-4 py-8 relative">
      {notif && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-sm bg-white border-l-4 border-green-600 shadow-2xl rounded-2xl px-4 py-3 flex items-start gap-3 animate-[slideDown_0.4s_ease-out]">
          <span className="text-2xl">💬</span>
          <div><p className="text-xs font-bold text-gray-700">Messages</p><p className="text-sm text-gray-600 mt-0.5">{notif}</p></div>
        </div>
      )}

      <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full px-6 py-8">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🌾</div>
          <h1 className="text-xl font-extrabold text-gray-900" style={{ fontFamily: "'Noto Sans Devanagari',sans-serif" }}>{t('appName')}</h1>
        </div>

        {step === 'details' ? (<>
          <div className="space-y-3 mb-4">
            <div className="flex items-center gap-2 border-2 border-gray-100 rounded-2xl px-4 py-3.5 bg-gray-50 focus-within:border-green-500 transition-colors">
              <input value={name} onChange={e => setName(e.target.value)} placeholder={t('namePlaceholder')}
                className="flex-1 outline-none bg-transparent text-base text-gray-900 placeholder-gray-400" />
              <MicButton language={language} onResult={txt => setName(txt)} size="w-9 h-9" />
            </div>
            <div className="flex items-center border-2 border-gray-100 rounded-2xl px-4 py-3.5 bg-gray-50 focus-within:border-green-500 transition-colors">
              <span className="text-gray-500 mr-2">🇮🇳 +91</span>
              <input type="tel" value={phone} onChange={e => setPhoneVal(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendOtp()}
                placeholder={t('phone')} maxLength={10}
                className="flex-1 outline-none bg-transparent text-base text-gray-900 placeholder-gray-400" />
            </div>
          </div>

          {/* FIX #3: floating game-style speech bubble instead of a plain box */}
          <div className="flex justify-center mb-5">
            <TutorialBubble text={currentHint} language={language} />
          </div>

          {error && <p className="text-red-500 text-sm mb-3 text-center">{error}</p>}
          <button onClick={sendOtp} disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold text-lg py-4 rounded-2xl shadow-lg active:scale-95 transition-all disabled:opacity-50">
            {loading ? '...' : t('sendOtp')}
          </button>
        </>) : (<>
          <button onClick={() => setStep('details')} className="flex items-center gap-2 text-gray-500 mb-5 text-sm hover:text-green-600">← {t('back')}</button>

          <div className="flex gap-3 justify-center mb-5">
            {otp.map((digit, i) => (
              <input key={i} ref={refs[i]} type="tel" maxLength={1} value={digit}
                onChange={e => handleOtpChange(i, e.target.value)}
                onKeyDown={e => { if (e.key === 'Backspace' && !digit && i > 0) refs[i - 1].current?.focus() }}
                className="w-14 h-16 text-center text-2xl font-bold border-2 border-gray-200 rounded-2xl outline-none focus:border-green-500 focus:ring-4 focus:ring-green-100 bg-gray-50 transition-all" />
            ))}
          </div>

          <div className="flex justify-center mb-5">
            <TutorialBubble text={currentHint} language={language} />
          </div>

          {countdown > 0
            ? <p className="text-center text-gray-400 text-sm mb-4">{t('resend')} ({countdown}s)</p>
            : <button onClick={sendOtp} className="w-full text-green-600 text-sm font-medium mb-4 hover:underline">{t('resend')}</button>}

          {error && <p className="text-red-500 text-sm mb-3 text-center font-medium">{error}</p>}
          <button onClick={verifyOtp} disabled={loading || otp.join('').length < 4}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold text-lg py-4 rounded-2xl shadow-lg active:scale-95 transition-all disabled:opacity-50">
            {loading ? '...' : t('verify')}
          </button>
        </>)}
      </div>
      <style jsx global>{`@keyframes slideDown { from { transform:translate(-50%,-120%);opacity:0 } to { transform:translate(-50%,0);opacity:1 } }`}</style>
    </div>
  )
}
