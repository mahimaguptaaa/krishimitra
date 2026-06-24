import type { Metadata } from 'next'
import './globals.css'
export const metadata: Metadata = { title: 'KrishiMitra', description: 'AI Assistant for Indian Farmers' }
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="hi" suppressHydrationWarning><body>{children}</body></html>
}
