'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import '@/i18n/config'
import { useAppStore } from '@/store/appStore'
import Sidebar from '@/components/Sidebar'

const HELPLINES = [
  { en: 'Kisan Call Center', hi: 'किसान कॉल सेंटर', number: '1800-180-1551', desc: 'Free toll-free helpline (24x7)' },
  { en: 'PM-KISAN Helpline', hi: 'PM-KISAN हेल्पलाइन', number: '155261', desc: 'PM-KISAN scheme queries' },
  { en: 'Crop Insurance Helpline', hi: 'फसल बीमा हेल्पलाइन', number: '1800-200-7710', desc: 'Pradhan Mantri Fasal Bima Yojana' },
  { en: 'Soil Health Card', hi: 'मृदा स्वास्थ्य कार्ड', number: '1800-180-1268', desc: 'Soil testing and health card' },
  { en: 'IFFCO Kisan', hi: 'इफको किसान', number: '1800-103-1967', desc: 'Fertilizer and farming advisory' },
  { en: 'Mandi Price Helpline', hi: 'मंडी भाव हेल्पलाइन', number: '1800-270-0224', desc: 'Live market price information' },
]

export default function HelplinePage() {
  const router = useRouter()
  const { t } = useTranslation()
  const { token, theme, language, sidebarOpen } = useAppStore()
  useEffect(() => { if (!token) router.replace('/') }, [token])
  useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark') }, [theme])
  const isDark = theme === 'dark'
  const useHindi = language === 'hi'

  return (
    <div className={`flex h-screen w-full overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      <Sidebar />
      <div className={`flex-1 overflow-y-auto transition-all ${sidebarOpen ? 'md:ml-64' : ''}`}>
        <header className={`flex items-center gap-3 px-4 py-3 border-b sticky top-0 z-30 backdrop-blur-md ${isDark ? 'bg-gray-950/90 border-gray-800' : 'bg-white/90 border-gray-100'} shadow-sm`}>
          <div className={sidebarOpen ? 'w-11' : 'w-0'} />
          <h1 className={`text-lg font-bold flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>{t('helplineTitle')} 📞</h1>
        </header>
        <div className="p-5 max-w-2xl mx-auto space-y-3">
          {HELPLINES.map(h => (
            <a key={h.number} href={`tel:${h.number}`} className={`flex items-center gap-4 rounded-2xl p-4 border transition-all hover:shadow-md ${isDark ? 'bg-gray-900 border-gray-800 hover:bg-gray-800' : 'bg-white border-gray-100'}`}>
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-xl flex-shrink-0">📞</div>
              <div className="min-w-0">
                <p className={`font-semibold text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>{useHindi ? h.hi : h.en}</p>
                <p className="text-green-600 font-bold text-lg mt-0.5">{h.number}</p>
                <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>{h.desc}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
