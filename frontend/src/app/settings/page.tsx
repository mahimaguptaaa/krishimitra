'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import '@/i18n/config'
import i18n from '@/i18n/config'
import { useAppStore } from '@/store/appStore'
import Sidebar from '@/components/Sidebar'
import { playInstructionAudio } from '@/lib/speech'
import { useState } from 'react'

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

export default function SettingsPage() {
  const router = useRouter()
  const { t } = useTranslation()
  const { token, language, theme, fontSize, voiceSpeed, setLanguage, setTheme, setFontSize, setVoiceSpeed, sidebarOpen } = useAppStore()
  const [playingCode, setPlayingCode] = useState<string | null>(null)

  useEffect(() => { if (!token) router.replace('/') }, [token])
  useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark') }, [theme])
  useEffect(() => { document.documentElement.style.fontSize = fontSize === 'small' ? '14px' : fontSize === 'large' ? '18px' : '16px' }, [fontSize])

  const isDark = theme === 'dark'
  const changeLanguage = (code: string) => { setLanguage(code); i18n.changeLanguage(code) }
  const previewVoice = (code: string, native: string) => {
    setPlayingCode(code)
    playInstructionAudio(native, code).then(() => setPlayingCode(null))
  }

  const Card = ({ children }: { children: React.ReactNode }) => (
    <div className={`rounded-2xl p-5 border shadow-sm ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'}`}>{children}</div>
  )

  return (
    <div className={`flex h-screen w-full overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      <Sidebar />
      <div className={`flex-1 overflow-y-auto transition-all ${sidebarOpen ? 'md:ml-64' : ''}`}>
        <header className={`flex items-center gap-3 px-4 py-3 border-b sticky top-0 z-30 backdrop-blur-md
          ${isDark ? 'bg-gray-950/90 border-gray-800' : 'bg-white/90 border-gray-100'} shadow-sm`}>
          <div className={sidebarOpen ? 'w-11' : 'w-0'} />
          <h1 className={`text-lg font-bold flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>{t('settingsNav')} ⚙️</h1>
        </header>

        <div className="p-5 max-w-2xl mx-auto space-y-4">
          <Card>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xl">{isDark ? '🌙' : '☀️'}</span>
                <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>{t('darkMode')}</span>
              </div>
              <button onClick={() => setTheme(isDark ? 'light' : 'dark')}
                className={`w-14 h-8 rounded-full transition-colors relative ${isDark ? 'bg-green-600' : 'bg-gray-200'}`}>
                <span className={`absolute top-1 left-1 w-6 h-6 rounded-full bg-white shadow-md transition-transform ${isDark ? 'translate-x-6' : ''}`} />
              </button>
            </div>
          </Card>

          {/* FIX #7: matches onboarding card style exactly — native + (English) + 🔊 preview */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xl">🌐</span>
              <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>{t('language')}</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {LANGUAGES.map(lang => (
                <button key={lang.code} onClick={() => changeLanguage(lang.code)}
                  className={`flex items-center justify-between rounded-2xl px-3 py-3 border-2 text-left transition-all
                    ${language === lang.code ? 'border-green-600 bg-green-50 dark:bg-green-950 shadow-md' : isDark ? 'border-gray-800 bg-gray-800' : 'border-gray-100 bg-gray-50 hover:border-green-300'}`}>
                  <div className="min-w-0">
                    <p className={`font-bold text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>{lang.native}</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>({lang.en})</p>
                  </div>
                  <button type="button" onClick={e => { e.stopPropagation(); previewVoice(lang.code, lang.native) }}
                    className={`w-7 h-7 rounded-full flex items-center justify-center ml-1 flex-shrink-0 transition-colors
                      ${playingCode === lang.code ? 'bg-green-600 text-white' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}>
                    🔊
                  </button>
                </button>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xl">🔊</span>
              <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>{t('voiceSpeed')}: {voiceSpeed}x</span>
            </div>
            <input type="range" min={0.5} max={2} step={0.25} value={voiceSpeed}
              onChange={e => setVoiceSpeed(parseFloat(e.target.value))} className="w-full accent-green-600" />
          </Card>

          <Card>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xl font-bold">T</span>
              <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>{t('fontSize')}</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {(['small', 'normal', 'large'] as const).map(f => (
                <button key={f} onClick={() => setFontSize(f)}
                  className={`py-3 rounded-xl text-sm font-medium transition-all
                    ${fontSize === f ? 'bg-green-600 text-white shadow-md' : isDark ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                  {f === 'small' ? t('small') : f === 'large' ? t('large') : t('normalSize')}
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
