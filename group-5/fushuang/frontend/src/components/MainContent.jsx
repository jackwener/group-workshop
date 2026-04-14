import { useState, useEffect } from 'react'

function MainContent({ session, apiBase }) {
  const [records, setRecords] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [selectedFileId, setSelectedFileId] = useState(null)

  // 获取问答记录
  useEffect(() => {
    if (!session?.session_id) {
      setRecords([])
      return
    }

    fetch(`${apiBase}/sessions/${session.session_id}/records`)
      .then(res => res.json())
      .then(data => setRecords(data.records || []))
      .catch(console.error)
  }, [session, apiBase])

  // 获取文件列表
  useEffect(() => {
    if (!session?.session_id) {
      setFiles([])
      return
    }

    // 轮询文件状态
    const pollFiles = async () => {
      try {
        // 这里需要后端提供获取会话文件的接口
        // 暂时使用模拟数据
        setFiles([])
      } catch (err) {
        console.error('获取文件列表失败:', err)
      }
    }

    pollFiles()
    const interval = setInterval(pollFiles, 3000)
    return () => clearInterval(interval)
  }, [session, apiBase])

  // 文件上传
  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file || !session) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('session_id', session.session_id)

    try {
      const res = await fetch(`${apiBase}/files/upload`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      
      if (data.file_id) {
        setFiles(prev => [...prev, data])
        setSelectedFileId(data.file_id)
        alert('文件上传成功，正在解析...')
      }
    } catch (err) {
      console.error('上传文件失败:', err)
      alert('上传失败')
    } finally {
      setUploading(false)
    }
  }

  // 提交问题
  const handleSubmit = async () => {
    if (!query.trim() || !session) return

    setLoading(true)
    try {
      const body = {
        query: query.trim(),
        session_id: session.session_id
      }
      if (selectedFileId) {
        body.file_id = selectedFileId
      }

      const res = await fetch(`${apiBase}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      const data = await res.json()
      
      if (data.answer) {
        // 刷新记录列表
        const recordsRes = await fetch(`${apiBase}/sessions/${session.session_id}/records`)
        const recordsData = await recordsRes.json()
        setRecords(recordsData.records || [])
        setQuery('')
      }
    } catch (err) {
      console.error('提交问题失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 按 Enter 发送
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const getSourceClass = (source) => {
    switch (source) {
      case 'copaw': return 'source-tag source-copaw'
      case 'bailian': return 'source-tag source-bailian'
      default: return 'source-tag source-demo'
    }
  }

  const getSourceText = (source) => {
    switch (source) {
      case 'copaw': return 'CoPaw'
      case 'bailian': return '百炼'
      default: return '离线演示'
    }
  }

  if (!session) {
    return (
      <main className="main-content">
        <div className="empty-state">请创建或选择一个会话开始</div>
      </main>
    )
  }

  return (
    <main className="main-content">
      <div className="content-area">
        {records.length === 0 ? (
          <div className="empty-state">
            <div>
              <p>这是一个新会话</p>
              <p style={{ marginTop: '8px', fontSize: '14px' }}>在下方输入您的问题</p>
            </div>
          </div>
        ) : (
          <div className="records-list">
            {records.map(record => (
              <div key={record.id} className="record-card">
                <div className="record-query">Q: {record.query}</div>
                <div className="record-answer">{record.answer}</div>
                <div className="record-meta">
                  <span className={getSourceClass(record.answer_source)}>
                    {getSourceText(record.answer_source)}
                  </span>
                  <span>{new Date(record.timestamp).toLocaleString('zh-CN')}</span>
                  <span>{record.response_time_ms}ms</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="input-area">
        <div className="file-upload-section" style={{ marginBottom: '12px' }}>
          <label className="file-upload-btn" style={{
            display: 'inline-block',
            padding: '8px 16px',
            background: '#f5f5f5',
            border: '1px dashed #ccc',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '13px',
            color: '#666'
          }}>
            {uploading ? '上传中...' : '📎 上传研报文件 (PDF/Word)'}
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
          </label>
          {files.length > 0 && (
            <select
              value={selectedFileId || ''}
            onChange={(e) => setSelectedFileId(e.target.value || null)}
              style={{
                marginLeft: '12px',
                padding: '8px 12px',
                border: '1px solid #e0e0e0',
                borderRadius: '6px',
                fontSize: '13px'
              }}
            >
              <option value="">不使用文件</option>
              {files.map(f => (
                <option key={f.file_id} value={f.file_id}>
                  {f.file_name} ({f.parse_status === 'completed' ? '已解析' : '解析中...'})
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="input-container">
          <textarea
            className="query-input"
            placeholder="请输入您的问题..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
          />
          <button
            className="send-btn"
            onClick={handleSubmit}
            disabled={loading || !query.trim()}
          >
            {loading ? '发送中...' : '发送'}
          </button>
        </div>
      </div>
    </main>
  )
}

export default MainContent
