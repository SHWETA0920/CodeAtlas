'use client'

import { Suspense } from 'react'
import ChatInterface from '@/components/ChatInterface'

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        Loading...
      </div>
    }>
      <ChatInterface />
    </Suspense>
  )
}
