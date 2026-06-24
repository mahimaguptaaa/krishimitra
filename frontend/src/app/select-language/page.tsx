'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/store/appStore'
import '@/i18n/config'
import i18n from '@/i18n/config'

// format: native script + (English name) — exactly as user requested
const LANGUAGES = [
  { code: 'hi', native: 'हिन्दी',    en: 'Hindi'     },
  { code: 'en', native: 'English',   en: 'English'   },
  { code: 'pa', native: 'ਪੰਜਾਬੀ',   en: 'Punjabi'   },
  { code: 'mr', native: 'मराठी',     en: 'Marathi'   },
  { code: 'bn', native: 'বাংলা',     en: 'Bengali'   },
  { code: 'ta', native: 'தமிழ்',     en: 'Tamil'     },
  { code: 'te', native: 'తెలుగు',    en: 'Telugu'    },
  { code: 'gu', native: 'ગુજરાતી',   en: 'Gujarati'  },
  { code: 'kn', native: 'ಕನ್ನಡ',     en: 'Kannada'   },
  { code: 'ml', native: 'മലയാളം',   en: 'Malayalam' },
]

export default function SelectLanguage() {
  const router = useRouter()
  const { setLanguage, setOnboarded } = useAppStore()
  const [selected, setSelected] = useState('hi')
  const [playingCode, setPlayingCode] = useState<string | null>(null)

  const playName = (code: string, name: string) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    setPlayingCode(code)
    const utt = new SpeechSynthesisUtterance(name)
    utt.lang = code + (code === 'en' ? '-GB' : '-IN')
    utt.onend = () => setPlayingCode(null)
    window.speechSynthesis.speak(utt)
  }

  const handleContinue = () => {
    setLanguage(selected)
    setOnboarded(true)
    i18n.changeLanguage(selected)
    router.push('/login')
  }

  const selectedLang = LANGUAGES.find(l => l.code === selected)

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-700 to-green-900 flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full px-6 py-8">
        {/* header */}
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">🌾</div>
          <h1 className="text-2xl font-extrabold text-gray-900"
              style={{ fontFamily: "'Noto Sans Devanagari',sans-serif" }}>कृषि-मित्र</h1>
          <p className="text-gray-400 text-sm mt-1">Choose your language / अपनी भाषा चुनें</p>
        </div>

        {/* language grid — native + (English) */}
        <div className="grid grid-cols-2 gap-2 mb-6">
          {LANGUAGES.map(lang => (
            <button key={lang.code} onClick={() => setSelected(lang.code)}
              className={`flex items-center justify-between rounded-2xl px-3 py-3 border-2 text-left transition-all
                ${selected === lang.code
                  ? 'border-green-600 bg-green-50 shadow-md scale-[1.02]'
                  : 'border-gray-100 bg-gray-50 hover:border-green-300'}`}>
              <div className="min-w-0">
                <p className="font-bold text-sm text-gray-900">{lang.native}</p>
                <p className="text-xs text-gray-400">({lang.en})</p>
              </div>
              {/* listen button */}
              <button type="button" onClick={e => { e.stopPropagation(); playName(lang.code, lang.native) }}
                className={`w-7 h-7 rounded-full flex items-center justify-center ml-1 flex-shrink-0 transition-colors
                  ${playingCode === lang.code ? 'bg-green-600 text-white' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}>
                🔊
              </button>
            </button>
          ))}
        </div>

        <button onClick={handleContinue}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-bold text-lg py-4 rounded-2xl shadow-lg active:scale-95 transition-all">
          {selectedLang?.native} में जारी रखें →
        </button>
      </div>
    </div>
  )
}