'use client'
import { useTranslation } from 'react-i18next'
import '@/i18n/config'
import i18n from '@/i18n/config'
import { useAppStore } from '@/store/appStore'
import { useRouter } from 'next/navigation'

const LANGUAGES = [
  {code:'hi',name:'हिन्दी',flag:'🇮🇳'},{code:'en',name:'English',flag:'🇬🇧'},
  {code:'pa',name:'ਪੰਜਾਬੀ',flag:'🇮🇳'},{code:'mr',name:'मराठी',flag:'🇮🇳'},
  {code:'bn',name:'বাংলা',flag:'🇮🇳'},{code:'ta',name:'தமிழ்',flag:'🇮🇳'},
  {code:'te',name:'తెలుగు',flag:'🇮🇳'},{code:'gu',name:'ગુજરાતી',flag:'🇮🇳'},
]

export default function SettingsPanel() {
  const { t } = useTranslation()
  const { language, theme, setLanguage, setTheme, logout } = useAppStore()
  const router = useRouter()
  const isDark = theme === 'dark'
  const bg  = isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'
  const txt = isDark ? 'text-white' : 'text-gray-900'
  const muted = isDark ? 'text-gray-400' : 'text-gray-500'

  const changeLanguage = (code: string) => {
    setLanguage(code)
    i18n.changeLanguage(code)
  }

  return (
    <div className={`h-full flex flex-col border-l ${bg} overflow-y-auto`}>
      <div className="p-4 border-b border-inherit flex items-center justify-between">
        <h2 className={`text-lg font-bold ${txt}`}>{t('settings')}</h2>
        <button onClick={() => router.back()} className={`${muted} hover:text-red-400 text-xl`}>✕</button>
      </div>

      <div className="p-4 space-y-6 flex-1">
        {/* Language */}
        <div>
          <p className={`text-xs font-semibold uppercase tracking-wide mb-3 ${muted}`}>{t('language')}</p>
          <div className="grid grid-cols-2 gap-2">
            {LANGUAGES.map(l => (
              <button key={l.code} onClick={() => changeLanguage(l.code)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-2xl border text-sm font-medium transition-all
                  ${language === l.code
                    ? 'border-green-500 bg-green-50 text-green-700 dark:bg-green-900 dark:text-green-300'
                    : isDark ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-200 text-gray-700 hover:bg-gray-50'}`}>
                <span>{l.flag}</span><span>{l.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Theme */}
        <div>
          <p className={`text-xs font-semibold uppercase tracking-wide mb-3 ${muted}`}>{t('theme')}</p>
          <div className="flex gap-2">
            {(['light','dark'] as const).map(th => (
              <button key={th} onClick={() => setTheme(th)}
                className={`flex-1 py-3 rounded-2xl border font-medium text-sm transition-all
                  ${theme === th
                    ? 'border-green-500 bg-green-50 text-green-700 dark:bg-green-900 dark:text-green-300'
                    : isDark ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-200 text-gray-700 hover:bg-gray-50'}`}>
                {th === 'light' ? '☀️ ' + t('light') : '🌙 ' + t('dark')}
              </button>
            ))}
          </div>
        </div>

        {/* Language selection redirect */}
        <div>
          <button onClick={() => { router.push('/select-language') }}
            className={`w-full py-3 rounded-2xl border text-sm font-medium transition-all
              ${isDark ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-200 text-gray-700 hover:bg-gray-50'}`}>
            🌍 Change Language Screen
          </button>
        </div>
      </div>

      {/* Logout */}
      <div className="p-4 border-t border-inherit">
        <button onClick={() => { logout(); window.location.href = '/' }}
          className="w-full py-3 rounded-2xl text-sm font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-950 transition-all border border-red-100 dark:border-red-900">
          🚪 {t('logout')}
        </button>
      </div>
    </div>
  )
}
