'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import '@/i18n/config'
import { useAppStore } from '@/store/appStore'
import Sidebar from '@/components/Sidebar'

export default function HistoryPage() {
  const router = useRouter()
  const { t } = useTranslation()
  const { token, theme, sessions, setActiveChat, deleteChat, updateChatTitle, sidebarOpen } = useAppStore()
  const [editId, setEditId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)

  useEffect(() => { if (!token) router.replace('/') }, [token])
  useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark') }, [theme])
  const isDark = theme === 'dark'
  const openChat = (id: string) => { setActiveChat(id); router.push('/chat') }

  return (
    <div className={`flex h-screen w-full overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      <Sidebar />
      <div className={`flex-1 overflow-y-auto transition-all ${sidebarOpen ? 'md:ml-64' : ''}`}>
        <header className={`flex items-center gap-3 px-4 py-3 border-b sticky top-0 z-30 backdrop-blur-md ${isDark ? 'bg-gray-950/90 border-gray-800' : 'bg-white/90 border-gray-100'} shadow-sm`}>
          <div className={sidebarOpen ? 'w-11' : 'w-0'} />
          <h1 className={`text-lg font-bold flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>🕐 {t('history')}</h1>
        </header>
        <div className="p-5 max-w-2xl mx-auto space-y-2">
          {sessions.length === 0 && <p className={`text-center py-16 text-sm ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>{t('chatHistoryEmpty')}</p>}
          {sessions.map(sess => (
            <div key={sess.id} className={`group rounded-2xl px-4 py-3.5 cursor-pointer transition-all border ${isDark ? 'bg-gray-900 border-gray-800 hover:bg-gray-800' : 'bg-white border-gray-100 hover:bg-green-50 hover:border-green-200 shadow-sm'}`}
              onClick={() => editId !== sess.id && openChat(sess.id)}>
              {editId === sess.id ? (
                <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                  <input value={editTitle} onChange={e => setEditTitle(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') { updateChatTitle(sess.id, editTitle); setEditId(null) } if (e.key === 'Escape') setEditId(null) }}
                    className={`flex-1 text-sm outline-none rounded-lg px-2 py-1 ${isDark ? 'bg-gray-800 text-white' : 'bg-gray-50 border'}`} autoFocus />
                  <button onClick={() => { updateChatTitle(sess.id, editTitle); setEditId(null) }} className="text-green-500 font-bold">✓</button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm font-medium truncate ${isDark ? 'text-white' : 'text-gray-900'}`}>{sess.title}</p>
                    <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{new Date(sess.createdAt).toLocaleDateString()}</p>
                  </div>
                  <div className="flex gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={e => { e.stopPropagation(); setEditTitle(sess.title); setEditId(sess.id) }} className="text-xs p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700">✏️</button>
                    <button onClick={e => { e.stopPropagation(); setDeleteId(sess.id) }} className="text-xs p-2 rounded hover:bg-red-100 text-red-400">🗑</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      {deleteId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[70] p-4">
          <div className={`rounded-2xl p-6 max-w-xs w-full shadow-xl ${isDark ? 'bg-gray-900' : 'bg-white'}`}>
            <p className={`text-base font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>{t('deleteConfirm')}</p>
            <div className="flex gap-3">
              <button onClick={() => { deleteChat(deleteId); setDeleteId(null) }} className="flex-1 bg-red-500 text-white py-3 rounded-2xl font-bold hover:bg-red-600">{t('yes')}</button>
              <button onClick={() => setDeleteId(null)} className={`flex-1 py-3 rounded-2xl font-bold border ${isDark ? 'border-gray-700 text-white' : 'border-gray-200 text-gray-700'}`}>{t('no')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
