'use client'

import { useState } from 'react'
import { FileCode, ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'

interface Source {
  file_path: string
  language: string
  chunk_type: string
  name: string
  start_line: number
  end_line: number
  score: number
}

const LANG_COLORS: Record<string, string> = {
  python:     'bg-blue-500/20 text-blue-300 border-blue-500/30',
  javascript: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  typescript: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
  go:         'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  rust:       'bg-orange-500/20 text-orange-300 border-orange-500/30',
  java:       'bg-red-500/20 text-red-300 border-red-500/30',
  cpp:        'bg-purple-500/20 text-purple-300 border-purple-500/30',
  default:    'bg-gray-500/20 text-gray-300 border-gray-500/30',
}

export default function SourceFiles({ sources }: { sources: Source[] }) {
  const [expanded, setExpanded] = useState(false)
  const visible = expanded ? sources : sources.slice(0, 3)

  return (
    <div className="mt-2">
      <p className="text-xs text-gray-600 mb-2 flex items-center gap-1">
        <FileCode className="w-3 h-3" />
        {sources.length} source{sources.length !== 1 ? 's' : ''} referenced
      </p>
      <div className="space-y-1.5">
        {visible.map((s, i) => {
          const langColor = LANG_COLORS[s.language] ?? LANG_COLORS.default
          const confidence = Math.round(s.score * 100)
          return (
            <div
              key={i}
              className="flex items-center gap-2 px-2.5 py-1.5 bg-gray-900 border border-gray-800 rounded-lg text-xs"
            >
              <span className={clsx('px-1.5 py-0.5 rounded border font-mono text-xs shrink-0', langColor)}>
                {s.language}
              </span>
              <span className="text-gray-400 font-mono truncate flex-1 min-w-0">
                {s.file_path}
              </span>
              <span className="text-gray-600 shrink-0">
                {s.name !== 'anonymous' && s.name ? `${s.chunk_type}: ${s.name}` : ''}
              </span>
              <span className="text-gray-600 shrink-0 font-mono">
                L{s.start_line}–{s.end_line}
              </span>
              <span className="text-indigo-500/70 shrink-0 font-mono">
                {confidence}%
              </span>
            </div>
          )
        })}
      </div>
      {sources.length > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-1.5 text-xs text-gray-600 hover:text-gray-400 flex items-center gap-1 transition-colors"
        >
          {expanded
            ? <><ChevronUp className="w-3 h-3" /> Show less</>
            : <><ChevronDown className="w-3 h-3" /> Show {sources.length - 3} more</>
          }
        </button>
      )}
    </div>
  )
}
