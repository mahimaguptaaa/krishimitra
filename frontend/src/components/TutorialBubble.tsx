'use client'
import { playInstructionAudio } from '@/lib/speech'

interface Props {
  text: string
  language: string
  position?: 'top' | 'bottom'
  className?: string
}

export default function TutorialBubble({ text, language, position = 'bottom', className = '' }: Props) {
  // FIX: now plays through the backend TTS engine first (correct
  // pronunciation for all 10 languages), falling back to the browser
  // voice only if the backend is unreachable.
  const speak = () => playInstructionAudio(text, language)

  return (
    <div className={`relative inline-block ${className}`}>
      <div className="relative bg-yellow-300 text-green-900 rounded-2xl px-4 py-3 shadow-xl
        animate-[bubbleIn_0.35s_cubic-bezier(0.34,1.56,0.64,1)_both] max-w-xs">
        {position === 'bottom' ? (
          <div className="absolute -top-2 left-8 w-4 h-4 bg-yellow-300 rotate-45 rounded-sm" />
        ) : (
          <div className="absolute -bottom-2 left-8 w-4 h-4 bg-yellow-300 rotate-45 rounded-sm" />
        )}
        <div className="flex items-start gap-2">
          <p className="text-sm font-medium leading-snug flex-1">{text}</p>
          <button onClick={speak}
            className="w-7 h-7 rounded-full bg-green-700 text-white flex items-center justify-center text-xs flex-shrink-0 hover:bg-green-800 transition-colors active:scale-90">
            🔊
          </button>
        </div>
      </div>
      <style jsx global>{`
        @keyframes bubbleIn {
          0%   { opacity: 0; transform: translateY(8px) scale(0.85); }
          100% { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
    </div>
  )
}
