'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Github, Upload, Brain, Zap, Search, Bug, ChevronRight, Loader2 } from 'lucide-react'
import { ingestGithub, ingestFiles, pollStatus } from '@/lib/api'

export default function HomePage() {
  const router = useRouter()
  const fileRef = useRef<HTMLInputElement>(null)
  const [githubUrl, setGithubUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  async function handleGithub(e: React.FormEvent) {
    e.preventDefault()
    if (!githubUrl.trim()) return
    setLoading(true); setError(''); setStatus('Cloning repository…')

    try {
      const { project_id } = await ingestGithub(githubUrl)
      await poll(project_id)
    } catch (err: any) {
      setError(err.message || 'Failed to ingest repo')
      setLoading(false)
    }
  }

  async function handleFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files
    if (!files || files.length === 0) return
    setLoading(true); setError(''); setStatus('Uploading files…')

    try {
      const { project_id } = await ingestFiles(Array.from(files))
      await poll(project_id)
    } catch (err: any) {
      setError(err.message || 'Failed to ingest files')
      setLoading(false)
    }
  }

  async function poll(projectId: string) {
    setStatus('Parsing & indexing code…')
    const job = await pollStatus(projectId, (msg) => setStatus(msg))
    router.push(`/chat?project=${projectId}`)
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16 relative overflow-hidden">
      {/* Background grid */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.04)_1px,transparent_1px)] bg-[size:60px_60px] pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-2xl">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-12 justify-center">
          <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30">
            <Brain className="w-7 h-7 text-indigo-400" />
          </div>
          <span className="text-2xl font-bold tracking-tight">
            Dev<span className="text-indigo-400">Brain</span> AI
          </span>
        </div>

        {/* Headline */}
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-4 leading-tight">
          Understand any codebase<br />
          <span className="text-indigo-400">in seconds</span>
        </h1>
        <p className="text-gray-400 text-center text-lg mb-12">
          Drop a GitHub repo or upload your project. Ask questions, debug, explore — like having a senior dev who&apos;s read every file.
        </p>

        {/* Input card */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleGithub} className="mb-6">
            <label className="block text-sm font-medium text-gray-400 mb-2">
              GitHub Repository URL
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Github className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="url"
                  value={githubUrl}
                  onChange={e => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/user/repo"
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-colors"
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading || !githubUrl.trim()}
                className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-medium text-sm transition-colors flex items-center gap-2 whitespace-nowrap"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ChevronRight className="w-4 h-4" />}
                Analyze
              </button>
            </div>
          </form>

          <div className="flex items-center gap-3 mb-6">
            <div className="h-px flex-1 bg-gray-800" />
            <span className="text-xs text-gray-600 uppercase tracking-wider">or</span>
            <div className="h-px flex-1 bg-gray-800" />
          </div>

          <input
            ref={fileRef} type="file" multiple
            accept=".zip,.py,.js,.ts,.jsx,.tsx,.go,.rs,.java,.cpp,.c,.h,.rb,.php,.cs,.md"
            className="hidden"
            onChange={handleFiles}
            disabled={loading}
          />
          <button
            onClick={() => fileRef.current?.click()}
            disabled={loading}
            className="w-full py-3 border border-dashed border-gray-700 hover:border-indigo-500/60 hover:bg-indigo-500/5 rounded-xl text-sm text-gray-400 hover:text-indigo-400 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload className="w-4 h-4" />
            Upload project files or .zip
          </button>

          {/* Status */}
          {loading && (
            <div className="mt-4 flex items-center gap-2 text-sm text-indigo-400">
              <Loader2 className="w-4 h-4 animate-spin shrink-0" />
              <span>{status}</span>
            </div>
          )}
          {error && (
            <div className="mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}
        </div>

        {/* Feature pills */}
        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { icon: Search, label: 'Smart Search' },
            { icon: Bug, label: 'Debug Assistant' },
            { icon: Zap, label: 'Code Optimizer' },
            { icon: Brain, label: 'Architecture Explainer' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-2 text-xs text-gray-500 bg-gray-900/60 border border-gray-800 rounded-lg px-3 py-2">
              <Icon className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              {label}
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
