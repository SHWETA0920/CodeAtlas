const BASE = '/api/backend'

// ── Ingest ────────────────────────────────────────────────────────────

export async function ingestGithub(githubUrl: string): Promise<{ project_id: string }> {
  const res = await fetch(`${BASE}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ github_url: githubUrl }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function ingestFiles(files: File[]): Promise<{ project_id: string }> {
  const form = new FormData()
  files.forEach(f => form.append('files[]', f, f.name))
  const res = await fetch(`${BASE}/ingest`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function pollStatus(
  projectId: string,
  onMessage?: (msg: string) => void,
  intervalMs = 1500,
  timeoutMs = 300000,
): Promise<void> {
  const start = Date.now()

  while (Date.now() - start < timeoutMs) {
    const res = await fetch(`${BASE}/ingest/status/${projectId}`)
    const data = await res.json()

    onMessage?.(data.message || data.status)

    if (data.status === 'ready') return
    if (data.status === 'error') throw new Error(data.message || 'Indexing failed')

    await sleep(intervalMs)
  }
  throw new Error('Indexing timed out')
}

// ── Query ─────────────────────────────────────────────────────────────

export async function queryStream(
  projectId: string,
  query: string,
  filterLanguage?: string,
  filterModule?: string,
  onToken?: (token: string) => void,
  onSources?: (sources: any[]) => void,
): Promise<void> {
  const res = await fetch(`${BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id:      projectId,
      query,
      stream:          true,
      filter_language: filterLanguage,
      filter_module:   filterModule,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error || `HTTP ${res.status}`)
  }

  const reader  = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer    = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6).trim()
      if (data === '[DONE]') return

      try {
        const parsed = JSON.parse(data)
        if (parsed.type === 'token') onToken?.(parsed.content)
        if (parsed.type === 'sources') onSources?.(parsed.sources)
      } catch {
        // ignore parse errors
      }
    }
  }
}

// ── Helpers ───────────────────────────────────────────────────────────

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}
