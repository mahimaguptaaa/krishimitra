import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message { id: string; role: 'user' | 'assistant'; content: string; imageUrl?: string; timestamp: number }
export interface ChatSession { id: string; title: string; messages: Message[]; createdAt: number }
export function uuidv4(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID()
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0; const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}
interface FarmerContext { location: string; crops: string[]; state: string }

interface AppState {
  token: string | null; phone: string | null; userName: string | null
  language: string
  onboarded: boolean
  farmerOnboarded: boolean
  farmerCtx: FarmerContext
  tutorialDone: boolean
  theme: 'light' | 'dark'; fontSize: 'small' | 'normal' | 'large'; voiceSpeed: number
  sessions: ChatSession[]; activeChatId: string | null; sidebarOpen: boolean

  setToken: (t: string | null) => void
  setPhone: (p: string) => void
  setUserName: (n: string) => void
  setLanguage: (l: string) => void
  setOnboarded: (v: boolean) => void
  setFarmerOnboarded: (v: boolean) => void
  setFarmerCtx: (c: FarmerContext) => void
  setTutorialDone: (v: boolean) => void
  setTheme: (t: 'light' | 'dark') => void
  setFontSize: (f: 'small' | 'normal' | 'large') => void
  setVoiceSpeed: (v: number) => void
  setSidebarOpen: (o: boolean) => void
  newChat: () => string
  setActiveChat: (id: string) => void
  addMessage: (chatId: string, msg: Message) => void
  updateChatTitle: (chatId: string, title: string) => void
  deleteChat: (chatId: string) => void
  logout: () => void
  activeMessages: () => Message[]
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      token: null, phone: null, userName: null,
      language: 'hi', onboarded: false, farmerOnboarded: false,
      farmerCtx: { location: '', crops: [], state: '' },
      tutorialDone: false,
      theme: 'light', fontSize: 'normal', voiceSpeed: 1,
      sessions: [], activeChatId: null, sidebarOpen: true,

      setToken: t => set({ token: t }),
      setPhone: p => set({ phone: p }),
      setUserName: n => set({ userName: n }),
      setLanguage: l => { localStorage.setItem('km_lang', l); set({ language: l }) },
      setOnboarded: v => set({ onboarded: v }),
      setFarmerOnboarded: v => set({ farmerOnboarded: v }),
      setFarmerCtx: c => set({ farmerCtx: c }),
      setTutorialDone: v => set({ tutorialDone: v }),
      setTheme: t => set({ theme: t }),
      setFontSize: f => set({ fontSize: f }),
      setVoiceSpeed: v => set({ voiceSpeed: v }),
      setSidebarOpen: o => set({ sidebarOpen: o }),

      newChat: () => {
        const id = uuidv4()
        set(s => ({ sessions: [{ id, title: 'New Chat', messages: [], createdAt: Date.now() }, ...s.sessions], activeChatId: id }))
        return id
      },
      setActiveChat: id => set({ activeChatId: id }),
      addMessage: (chatId, msg) => set(s => ({
        sessions: s.sessions.map(sess => sess.id !== chatId ? sess : {
          ...sess, messages: [...sess.messages, msg],
          title: sess.messages.length === 0 && msg.role === 'user' ? msg.content.slice(0, 40) : sess.title,
        })
      })),
      updateChatTitle: (chatId, title) => set(s => ({ sessions: s.sessions.map(sess => sess.id === chatId ? { ...sess, title } : sess) })),
      deleteChat: chatId => set(s => {
        const sessions = s.sessions.filter(x => x.id !== chatId)
        return { sessions, activeChatId: s.activeChatId === chatId ? (sessions[0]?.id || null) : s.activeChatId }
      }),

      // FIX: logout resets onboarded + farmerOnboarded + language is NOT
      // wiped (kept neutral) but onboarding screens will show again so a
      // new number doesn't inherit the previous farmer's saved entries.
      logout: () => set({
        token: null, phone: null, userName: null,
        onboarded: false, farmerOnboarded: false,
        farmerCtx: { location: '', crops: [], state: '' },
        tutorialDone: false,
        sessions: [], activeChatId: null,
      }),

      activeMessages: () => {
        const s = get()
        return s.sessions.find(x => x.id === s.activeChatId)?.messages || []
      },
    }),
    { name: 'krishimitra-store', partialize: s => ({
      token: s.token, phone: s.phone, userName: s.userName,
      language: s.language, onboarded: s.onboarded,
      farmerOnboarded: s.farmerOnboarded, farmerCtx: s.farmerCtx,
      tutorialDone: s.tutorialDone,
      theme: s.theme, fontSize: s.fontSize, voiceSpeed: s.voiceSpeed,
      sessions: s.sessions, activeChatId: s.activeChatId,
    })}
  )
)
