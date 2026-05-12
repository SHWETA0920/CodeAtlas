'use client'

import { useSearchParams, useRouter } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'
import { Brain, Send, ArrowLeft, Filter, Loader2, Code2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import SourceFiles from '@/components/SourceFiles'
import { queryStream } from '@/lib/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  streaming?: boolean
}

interface Source {
  file_path: string
  language: string
  chunk_type: string
  name: string
  start_line: number
  end_line: number
  score: number
}

const EXAMPLE_QUERIES = [
  'Explain the overall project architecture',
  'Where is authentication handled?',
  'How does error handling work?',
  'What database models are defined?',
  'Show me the main entry point',
]

export default function ChatInterface() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const projectId = searchParams.get('project') || ''

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [filterLang, setFilterLang] = useState('')
  const [filterModule, setFilterModule] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(queryText?: string) {
    const q = (queryText ?? input).trim()
    if (!q || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setLoading(true)

    // Add placeholder assistant message
    setMessages(prev => [...prev, {
      role: 'assistant', content: '', streaming: true, sources: []
    }])

    try {
      await queryStream(
        projectId, q,
        filterLang || undefined,
        filterModule || undefined,
        (token) => {
          setMessages(prev => {
            const updated = [...prev]
            const last = updated[updated.length - 1]
            if (last.role === 'assistant') {
              last.content += token
            }
            return updated
          })
        },
        (sources) => {
          setMessages(prev => {
            const updated = [...prev]
            const last = updated[updated.length - 1]
            if (last.role === 'assistant') {
              last.sources = sources
            }
            return updated
          })
        }
      )
    } catch (err: any) {
      setMessages(prev => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last.role === 'assistant') {
          last.content = `Error: ${err.message}`
        }
        return updated
      })
    } finally {
      setMessages(prev => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last.role === 'assistant') last.streaming = false
        return updated
      })
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-950">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-gray-800 bg-gray-900/80 backdrop-blur shrink-0">
        <button
          onClick={() => router.push('/')}
          className="p-1.5 hover:bg-gray-800 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-gray-400" />
        </button>
        <div className="p-1.5 rounded-lg bg-indigo-500/20">
          <Brain className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">CodeAtlas</p>
          <p className="text-xs text-gray-500 truncate font-mono">{projectId}</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`p-1.5 rounded-lg transition-colors ${showFilters ? 'bg-indigo-500/20 text-indigo-400' : 'hover:bg-gray-800 text-gray-400'}`}
        >
          <Filter className="w-4 h-4" />
        </button>
      </header>

      {/* Filters dropdown */}
      {showFilters && (
        <div className="px-4 py-3 bg-gray-900 border-b border-gray-800 flex gap-3 shrink-0">
          <input
            type="text"
            placeholder="Filter language (e.g. python)"
            value={filterLang}
            onChange={e => setFilterLang(e.target.value)}
            className="flex-1 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-indigo-500"
          />
          <input
            type="text"
            placeholder="Filter module (e.g. auth)"
            value={filterModule}
            onChange={e => setFilterModule(e.target.value)}
            className="flex-1 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-indigo-500"
          />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-6">
            <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
              <Code2 className="w-8 h-8 text-indigo-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold mb-1">Codebase is ready</h2>
              <p className="text-sm text-gray-500">Ask anything about your project</p>
            </div>
            <div className="grid grid-cols-1 gap-2 w-full max-w-md">
              {EXAMPLE_QUERIES.map(q => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="text-left px-4 py-2.5 bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-gray-700 rounded-xl text-sm text-gray-400 hover:text-gray-200 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="p-1.5 rounded-lg bg-indigo-500/20 h-fit shrink-0 mt-0.5">
                <Brain className="w-3.5 h-3.5 text-indigo-400" />
              </div>
            )}

            <div className={`max-w-3xl ${msg.role === 'user' ? 'max-w-lg' : 'flex-1'}`}>
              {msg.role === 'user' ? (
                <div className="bg-indigo-600/20 border border-indigo-500/30 rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm text-gray-100">
                  {msg.content}
                </div>
              ) : (
                <div>
                  <div className={`text-sm text-gray-200 answer-prose ${msg.streaming && !msg.content ? 'typing-cursor' : ''} ${msg.streaming && msg.content ? 'typing-cursor' : ''}`}>
                    {msg.content ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    ) : (
                      <span className="text-gray-500">Thinking…</span>
                    )}
                  </div>
                  {msg.sources && msg.sources.length > 0 && !msg.streaming && (
                    <div className="mt-3">
                      <SourceFiles sources={msg.sources} />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 px-4 py-4 border-t border-gray-800 bg-gray-900/80 backdrop-blur">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your codebase… (Enter to send, Shift+Enter for newline)"
              rows={1}
              disabled={loading}
              className="w-full px-4 py-3 pr-12 bg-gray-800 border border-gray-700 rounded-xl text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 resize-none transition-colors disabled:opacity-50"
              style={{ minHeight: '48px', maxHeight: '160px' }}
            />
          </div>
          <button
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="px-4 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl transition-colors"
          >
            {loading
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <Send className="w-4 h-4" />
            }
          </button>
        </div>
        <p className="text-center text-xs text-gray-700 mt-2">
          DevBrain AI uses RAG over your codebase. Answers may not be perfect — always verify.
        </p>
      </div>
    </div>
  )
}
