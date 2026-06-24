'use client'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAppStore } from '@/store/appStore'
import { useTranslation } from 'react-i18next'
import '@/i18n/config'

const NAV = [
  { href: '/chat',     icon: '🏠', key: 'home'        },
  { href: '/history',  icon: '🕐', key: 'history'     },
  { href: '/helpline', icon: '📞', key: 'helpline'    },
  { href: '/settings', icon: '⚙️', key: 'settingsNav' },
]

export default function Sidebar() {
  const { t } = useTranslation()
  const path = usePathname()
  const router = useRouter()
  const { userName, farmerCtx, logout, sidebarOpen, setSidebarOpen } = useAppStore()

  return (
    <>
      {!sidebarOpen && (
        <button onClick={() => setSidebarOpen(true)}
          className="fixed top-4 left-4 z-50 w-11 h-11 rounded-full bg-green-700 hover:bg-green-800 text-white shadow-lg flex items-center justify-center transition-all">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
      )}

      {/* Backdrop only for small screens -- on desktop the sidebar
          doesn't need a dismiss-on-outside-click since it has an
          explicit close button (fix #7 below). */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 md:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={`fixed top-0 bottom-0 left-0 z-50 w-72 md:w-64 bg-green-900 flex flex-col
        transition-transform duration-300 ease-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>

        <div className="p-4 flex items-center gap-3 border-b border-green-800">
          <div className="w-11 h-11 rounded-full bg-yellow-400 flex items-center justify-center text-2xl flex-shrink-0">🌱</div>
          <div className="min-w-0 flex-1">
            <p className="text-white font-bold text-base truncate" style={{ fontFamily: "'Noto Sans Devanagari',sans-serif" }}>{t('appName')}</p>
            <p className="text-green-300 text-xs truncate">{userName || 'Farmer'}{farmerCtx?.location ? ` · ${farmerCtx.location}` : ''}</p>
          </div>
          {/* Explicit close button -- the ONLY way the sidebar closes now */}
          <button onClick={() => setSidebarOpen(false)}
            className="w-8 h-8 rounded-full bg-green-800 hover:bg-green-700 flex items-center justify-center text-white text-sm flex-shrink-0 transition-colors">
            ✕
          </button>
        </div>

        <nav className="flex-1 p-3 space-y-1 mt-1">
          {NAV.map(n => (
            // FIX #7: removed onClick={() => setSidebarOpen(false)} that
            // was here before -- clicking a nav item used to auto-close
            // the sidebar. Now it stays open until the ✕ button is used.
            <Link key={n.href} href={n.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-[15px] transition-colors
                ${path === n.href ? 'bg-green-700 text-white font-semibold shadow-sm' : 'text-green-100 hover:bg-green-800'}`}>
              <span className="text-lg">{n.icon}</span><span>{t(n.key)}</span>
            </Link>
          ))}
        </nav>

        {(farmerCtx?.location || farmerCtx?.crops?.length > 0) && (
          <div className="mx-3 mb-2 bg-green-800 rounded-xl px-3 py-2.5 text-xs text-green-200">
            {farmerCtx.location && <p>📍 {farmerCtx.location}</p>}
            {farmerCtx.crops?.length > 0 && <p className="mt-0.5">🌱 {farmerCtx.crops.slice(0, 3).join(', ')}</p>}
          </div>
        )}

        <div className="p-3 border-t border-green-800">
          <button onClick={() => { logout(); router.push('/') }}
            className="w-full flex items-center gap-2 px-4 py-3 rounded-xl text-red-300 hover:bg-green-800 hover:text-red-200 text-sm font-medium transition-colors">
            <span>↩</span> {t('logout')}
          </button>
        </div>
      </aside>
    </>
  )
}
