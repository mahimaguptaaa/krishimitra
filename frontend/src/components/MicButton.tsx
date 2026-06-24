'use client'
import { useState, useRef } from 'react'
import api from '@/lib/api'

export default function MicButton({ language, onResult, size = 'w-10 h-10' }:
  { language: string; onResult: (text: string) => void; size?: string }) {
  const [recording, setRecording] = useState(false)
  const [busy, setBusy] = useState(false)
  const recRef = useRef<MediaRecorder | null>(null)
  const chunks = useRef<BlobPart[]>([])

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
      chunks.current = []
      rec.ondataavailable = e => chunks.current.push(e.data)
      rec.onstop = async () => {
        setRecording(false)
        const blob = new Blob(chunks.current, { type: 'audio/webm' })
        const form = new FormData()
        form.append('audio', blob, 'voice.webm')
        form.append('language', language)   // always send current UI language
        setBusy(true)
        try {
          const res = await api.post('/api/voice/stt', form, { headers: { 'Content-Type': 'multipart/form-data' } })
          if (res.data.text) onResult(res.data.text)
        } catch {} finally { setBusy(false) }
      }
      recRef.current = rec; rec.start(); setRecording(true)
      setTimeout(() => rec.state === 'recording' && rec.stop(), 8000)
    } catch { alert('Microphone access denied. Please type instead.') }
  }
  const stop = () => { recRef.current?.stop(); recRef.current?.stream.getTracks().forEach(t => t.stop()) }

  return (
    <button type="button" onClick={recording ? stop : start} disabled={busy}
      className={`${size} rounded-full flex items-center justify-center transition-all flex-shrink-0
        ${recording ? 'bg-red-500 text-white animate-pulse' : 'bg-yellow-400 hover:bg-yellow-500 text-green-900'}`}>
      {busy ? '⏳' : recording ? '⏹' : '🎤'}
    </button>
  )
}
