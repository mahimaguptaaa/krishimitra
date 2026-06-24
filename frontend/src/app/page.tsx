'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/store/appStore'

export default function Splash() {
  const router = useRouter()
  const { token, onboarded, farmerOnboarded } = useAppStore()
  const [show, setShow] = useState(false)

  useEffect(() => {
    // Show splash for 2.5 s then route
    setShow(true)
    const t = setTimeout(() => {
      if (!onboarded) router.replace('/select-language')
      else if (!token) router.replace('/login')
      else if (!farmerOnboarded) router.replace('/onboarding')
      else router.replace('/chat')
    }, 2500)
    return () => clearTimeout(t)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-700 to-green-900 flex flex-col items-center justify-center">
      {/* animated logo */}
      <div className={`transition-all duration-700 ${show ? 'opacity-100 scale-100' : 'opacity-0 scale-75'} text-center`}>
        <div className="text-8xl mb-4 drop-shadow-lg">🌾</div>
        {/* Big Hindi name */}
        <h1 className="text-5xl font-extrabold text-white tracking-wide drop-shadow-md"
            style={{ fontFamily: "'Noto Sans Devanagari', sans-serif" }}>
          कृषि-मित्र
        </h1>
        <p className="text-yellow-300 text-xl font-semibold mt-2">KrishiMitra</p>
        <p className="text-green-200 text-base mt-1">किसानों का AI साथी</p>
        <div className="mt-10 flex gap-2 justify-center">
          {[0,1,2].map(i => (
            <div key={i} className="w-2.5 h-2.5 rounded-full bg-yellow-400 animate-bounce"
              style={{ animationDelay: `${i * 0.2}s` }} />
          ))}
        </div>
      </div>
    </div>
  )
}