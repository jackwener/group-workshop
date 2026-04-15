import { useState, useEffect } from 'react'

function App() {
  const [capabilities, setCapabilities] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/v1/compliance/capabilities')
      .then(res => res.json())
      .then(data => {
        setCapabilities(data)
        setLoading(false)
      })
      .catch(err => {
        setError('无法连接后端服务')
        setLoading(false)
      })
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#004098',
        color: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>研报合规稽核系统</h1>
        <p style={{ margin: '8px 0 0', opacity: 0.8 }}>Report Compliance Audit System</p>
      </header>

      {/* Main Content */}
      <main style={{
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <h2 style={{ margin: '0 0 16px', color: '#333' }}>系统状态</h2>

        {loading && <p style={{ color: '#666' }}>正在连接后端...</p>}

        {error && (
          <div style={{
            padding: '12px',
            backgroundColor: '#fff3f3',
            border: '1px solid #ffccc',
            borderRadius: '4px',
            color: '#d32f2f'
          }}>
            ⚠️ {error}
          </div>
        )}

        {capabilities && (
          <div style={{
            padding: '16px',
            backgroundColor: '#f0f7ff',
            border: '1px solid #b3d7ff',
            borderRadius: '4px'
          }}>
            <p style={{ margin: '0 0 8px', color: '#004098' }}>
              ✅ 后端连接成功
            </p>
            <p style={{ margin: '0 0 8px', color: '#333' }}>
              <strong>服务名称：</strong>{capabilities.service}
            </p>
            <p style={{ margin: '0 0 8px', color: '#333' }}>
              <strong>版本：</strong>{capabilities.version}
            </p>
            <p style={{ margin: 0, color: '#333' }}>
              <strong>功能模块：</strong>
              <span style={{
                display: 'inline-block',
                marginLeft: '8px',
                padding: '4px 12px',
                backgroundColor: '#e3f2fd',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                {capabilities.features?.join(' | ')}
              </span>
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: '20px',
        textAlign: 'center',
        color: '#888',
        fontSize: '14px'
      }}>
        <p>Frontend: Port 5173 | Backend: Port 5000</p>
      </footer>
    </div>
  )
}

export default App
