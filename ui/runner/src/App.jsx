import { useState } from 'react'
import { Send, Terminal, Image as ImageIcon, ExternalLink, AlertCircle, Loader2 } from 'lucide-react'

// Backend Configuration
const getApiBase = () => {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host.startsWith('192.168.') || host.startsWith('172.')) {
    // Prefer 127.0.0.1 over localhost to avoid IPv6 issues
    return `http://${host === 'localhost' ? '127.0.0.1' : host}:8000`;
  }
  return `${window.location.protocol}//${host}`;
};

const API_BASE = getApiBase();
console.log('Using API_BASE:', API_BASE);

function App() {
  const [jsonInput, setJsonInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState([])

  const handleRun = async () => {
    setError(null)
    setIsLoading(true)
    setResults([])

    // 1. Client-side Validation
    let parsedJson
    try {
      parsedJson = JSON.parse(jsonInput)
    } catch (e) {
      setError('JSON inválido: Por favor revisa la sintaxis (comas, llaves, etc.)')
      setIsLoading(false)
      return
    }

    // 2. API Call
    try {
      const response = await fetch(`${API_BASE}/nanobanana/run-full`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedJson),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error Response:', errorData);
        throw new Error(`Error HTTP: ${response.status} - ${JSON.stringify(errorData.detail || errorData)}`);
      }

      const data = await response.json()

      if (data.status === 'ERROR') {
        setError(data.error || 'El motor devolvió un error desconocido.')
      } else {
        setResults(data.results || [])
      }
    } catch (err) {
      setError(`Error de red o servidor: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="runner-container">
      <header className="header">
        <h1>NanoBanana Runner</h1>
        <p>Generación de imágenes con control absoluto.</p>
      </header>

      <main className="runner-main">
        {/* Input Section */}
        <section className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: '#10b981' }}>
            <Terminal size={18} />
            <span style={{ fontSize: '0.9rem', fontWeight: 600, letterSpacing: '0.05em' }}>INPUT_SPEC.JSON</span>
          </div>
          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            placeholder="Pega aquí el JSON del storyboard (NanoBananaPro)..."
            spellCheck="false"
          />
          <div className="controls">
            <button onClick={handleRun} disabled={isLoading || !jsonInput.trim()}>
              {isLoading ? (
                <>
                  <div className="spinner" />
                  <span>Procesando...</span>
                </>
              ) : (
                <>
                  <Send size={18} />
                  <span>Ejecutar Pipeline</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="error-message">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={20} />
                <strong>Error</strong>
              </div>
              <p style={{ margin: '0.5rem 0 0 1.7rem' }}>{error}</p>
            </div>
          )}
        </section>

        {/* Results Section */}
        <section style={{ marginTop: '3rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
            <ImageIcon className="text-banana" size={24} style={{ color: '#fcd34d' }} />
            <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Resultados</h2>
          </div>

          {results.length > 0 ? (
            <div className="results-grid">
              {results.map((res, idx) => (
                <div key={`${res.task_id}-${idx}`} className="glass-panel task-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3>{res.task_id} {res.variant > 1 && `(v${res.variant})`}</h3>
                    <a href={res.image_url} target="_blank" rel="noreferrer" className="asset-badge">
                      <ExternalLink size={14} />
                    </a>
                  </div>

                  <div className="image-preview">
                    <img src={res.image_url} alt={res.task_id} loading="lazy" />
                  </div>

                  <div className="prompt-box">
                    {res.final_prompt}
                  </div>

                  {res.assets_sent && res.assets_sent.length > 0 && (
                    <div className="assets-section">
                      <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#64748b', marginBottom: '0.5rem', fontWeight: 700 }}>
                        Assets / References
                      </p>
                      <div className="assets-list">
                        {res.assets_sent.map((asset, aIdx) => (
                          <a
                            key={aIdx}
                            href={asset.resolved_url}
                            target="_blank"
                            rel="noreferrer"
                            className="asset-badge"
                            title={asset.resolved_url}
                          >
                            {asset.ref_id}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            !isLoading && (
              <div className="no-results">
                <p>No hay resultados que mostrar. Pega un JSON y presiona "Ejecutar Pipeline".</p>
              </div>
            )
          )}
        </section>
      </main>

      <footer style={{ marginTop: '4rem', padding: '2rem', borderTop: '1px solid var(--border-color)', textAlign: 'center', color: '#475569', fontSize: '0.8rem' }}>
        <p>© 2025 Hintsly Video Factory — NanoBananaPro Engine v1.0</p>
      </footer>
    </div>
  )
}

export default App
