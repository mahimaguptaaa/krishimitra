// Strips markdown symbols before sending text to TTS (issue #8: AI was
// reading "-", "*", "#" etc out loud). Mirrors backend/utils/text_clean.py
// so cleanup happens whichever path is used (backend gTTS or browser
// speechSynthesis fallback).
export function cleanForSpeech(text: string): string {
  if (!text) return text
  let cleaned = text

  cleaned = cleaned.replace(/\*\*(.+?)\*\*/g, '$1')
  cleaned = cleaned.replace(/\*(.+?)\*/g, '$1')
  cleaned = cleaned.replace(/^#{1,6}\s*/gm, '')
  cleaned = cleaned.replace(/^[\-\*\u2022]\s+/gm, '')
  cleaned = cleaned.replace(/^\d+[\.\)]\s+/gm, '')
  cleaned = cleaned.replace(/`([^`]*)`/g, '$1')
  cleaned = cleaned.replace(/\[(.*?)\]\((.*?)\)/g, '$1')
  cleaned = cleaned.replace(/[#_~|>]+/g, ' ')
  cleaned = cleaned.replace(/[ \t]+/g, ' ')
  cleaned = cleaned.replace(/\n{2,}/g, '. ')
  cleaned = cleaned.replace(/\n/g, '. ')
  cleaned = cleaned.replace(/\.\s*\./g, '.')

  return cleaned.trim()
}
