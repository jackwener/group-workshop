import { useState, useRef } from 'react'
import ReportDetail from './ReportDetail'

function ReportList({ reports, currentReport, setCurrentReport, setReports, loadReports }) {
  const [searchKeyword, setSearchKeyword] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef(null)

  const handleSearch = (keyword) => {
    setSearchKeyword(keyword)
    const params = keyword ? `?keyword=${encodeURIComponent(keyword)}` : ''
    fetch(`/api/v1/agent/reports${params}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) setReports(data.data.items || [])
      })
      .catch(err => console.error('Search failed:', err))
  }

  const handleUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const ext = file.name.toLowerCase().split('.').pop()
    if (!['pdf', 'html', 'htm'].includes(ext)) {
      alert('不支持的文件格式，仅支持 PDF/HTML')
      return
    }
    if (file.size > 50 * 1024 * 1024) {
      alert('文件过大，请限制在 50MB 以内')
      return
    }

    setUploading(true)
    setUploadProgress(0)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', file.name)

    fetch('/api/v1/agent/reports', { method: 'POST', body: formData })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          loadReports()
          setUploadProgress(100)
        } else if (data.error) {
          const code = data.error.code
          if (code === 'INVALID_FILE_TYPE') alert('不支持的文件格式，仅支持 PDF/HTML')
          else if (code === 'FILE_TOO_LARGE') alert('文件过大，请限制在 50MB 以内')
          else alert(data.error.message)
        }
      })
      .catch(err => { console.error('Upload failed:', err); alert('上传失败') })
      .finally(() => { setUploading(false); setUploadProgress(0); e.target.value = '' })
  }

  const handleMark = (reportId, isMarked) => {
    fetch(`/api/v1/agent/reports/${reportId}/mark`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_marked: !isMarked, mark_status: !isMarked ? 'important' : 'none' })
    })
      .then(res => res.json())
      .then(() => loadReports())
      .catch(err => console.error('Mark failed:', err))
  }

  const handleParse = (reportId) => {
    fetch(`/api/v1/agent/reports/${reportId}/parse`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          loadReports()
          if (currentReport?.report_id === reportId) {
            handleViewDetail(reportId)
          }
        } else {
          alert(data.error?.message || '解析失败')
        }
      })
      .catch(err => console.error('Parse failed:', err))
  }

  const handleDelete = (reportId) => {
    if (!window.confirm('确定删除该研报？')) return
    fetch(`/api/v1/agent/reports/${reportId}`, { method: 'DELETE' })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          loadReports()
          if (currentReport?.report_id === reportId) setCurrentReport(null)
        }
      })
      .catch(err => console.error('Delete failed:', err))
  }

  const handleViewDetail = (reportId) => {
    fetch(`/api/v1/agent/reports/${reportId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) setCurrentReport(data.data)
      })
      .catch(err => console.error('Failed to load report:', err))
  }

  const getRatingBadge = (report) => {
    const rating = report.parsed_result?.rating
    if (!rating) return null
    const colors = {
      '买入': 'bg-red-100 text-red-800',
      '增持': 'bg-orange-100 text-orange-800',
      '中性': 'bg-yellow-100 text-yellow-800',
      '减持': 'bg-blue-100 text-blue-800',
      '卖出': 'bg-green-100 text-green-800',
    }
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[rating] || 'bg-gray-100 text-gray-800'}`}>
        {rating}
      </span>
    )
  }

  if (currentReport) {
    return (
      <ReportDetail
        report={currentReport}
        onBack={() => setCurrentReport(null)}
        onMark={handleMark}
        onParse={handleParse}
        onDelete={handleDelete}
      />
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-slate-50 to-slate-100/50">
      {/* 工具栏 */}
      <div className="flex items-center justify-between mb-6">
        <input
          type="text"
          value={searchKeyword}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="搜索研报..."
          className="w-64 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100 bg-slate-50/50 placeholder:text-slate-300"
        />
        <div>
          <input ref={fileInputRef} type="file" accept=".pdf,.html,.htm" onChange={handleUpload} className="hidden" />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="btn-primary disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 disabled:shadow-none disabled:cursor-not-allowed"
          >
            {uploading ? `上传中... ${uploadProgress}%` : '上传研报'}
          </button>
        </div>
      </div>

      {/* 进度条 */}
      {uploading && (
        <div className="mb-4 w-full bg-slate-200 rounded-full h-2">
          <div className="bg-brand-500 h-2 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
        </div>
      )}

      {/* 研报列表 */}
      {reports.length === 0 ? (
        <div className="text-center text-slate-400 py-12">
          <p className="text-lg font-medium">暂无研报</p>
          <p className="text-sm mt-2 text-slate-300">点击「上传研报」添加 PDF/HTML 文件</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map(report => (
            <div
              key={report.report_id}
              className="bg-white rounded-xl border border-slate-100 p-4 hover:shadow-card-hover transition-all duration-200 cursor-pointer"
              onClick={() => handleViewDetail(report.report_id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-medium text-slate-700 truncate">{report.title}</h3>
                    {getRatingBadge(report)}
                    {report.is_marked && (
                      <span className="text-brand-500 text-sm">★</span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {report.file_type.toUpperCase()} · {(report.file_size / 1024).toFixed(1)}KB · {report.status}
                    {report.uploaded_at && ` · ${new Date(report.uploaded_at).toLocaleDateString()}`}
                  </p>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleMark(report.report_id, report.is_marked) }}
                    className={`text-sm ${report.is_marked ? 'text-brand-500' : 'text-slate-300 hover:text-brand-500'}`}
                    title="标记"
                  >★</button>
                  {report.status === 'pending' && (
                    <button
                      onClick={(e) => { e.stopPropagation(); handleParse(report.report_id) }}
                      className="text-xs text-brand-500 hover:text-brand-700 font-medium"
                    >解析</button>
                  )}
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(report.report_id) }}
                    className="text-slate-400 hover:text-rose-500"
                  >×</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ReportList
