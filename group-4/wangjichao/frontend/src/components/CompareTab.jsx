import { useState } from 'react'

function CompareTab({ reports, loadReports }) {
  const [selectedIds, setSelectedIds] = useState([])
  const [compareResult, setCompareResult] = useState(null)
  const [isComparing, setIsComparing] = useState(false)

  const toggleSelect = (reportId) => {
    setSelectedIds(prev =>
      prev.includes(reportId)
        ? prev.filter(id => id !== reportId)
        : prev.length < 10
          ? [...prev, reportId]
          : prev
    )
  }

  const handleCompare = () => {
    if (selectedIds.length < 2) {
      alert('请选择2-10份研报进行对比')
      return
    }
    setIsComparing(true)
    fetch('/api/v1/agent/reports/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report_ids: selectedIds })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setCompareResult(data.data)
        } else {
          const code = data.error?.code
          if (code === 'INVALID_REPORT_SELECTION') alert('请选择2-10份研报进行对比')
          else alert(data.error?.message || '对比失败')
        }
      })
      .catch(err => { console.error('Compare failed:', err); alert('对比失败') })
      .finally(() => setIsComparing(false))
  }

  const handleExport = () => {
    if (!compareResult) return
    const { headers, rows } = compareResult
    let csv = headers.join(',') + '\n'
    rows.forEach(row => {
      csv += headers.map(h => {
        const val = row[h]
        if (Array.isArray(val)) return `"${val.join('; ')}"`
        return `"${val || ''}"`
      }).join(',') + '\n'
    })
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `研报对比_${new Date().toLocaleDateString()}.csv`
    link.click()
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-slate-50 to-slate-100/50">
      {/* 研报选择器 */}
      <div className="glass-card p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-md font-bold text-slate-800">选择研报进行对比</h3>
          <span className="text-sm text-slate-400">已选 {selectedIds.length}/10</span>
        </div>
        {reports.length === 0 ? (
          <p className="text-slate-400 text-sm">暂无研报，请先上传</p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {reports.map(report => (
              <label
                key={report.report_id}
                className="flex items-center p-2.5 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(report.report_id)}
                  onChange={() => toggleSelect(report.report_id)}
                  className="mr-3 rounded border-slate-300 text-brand-500 focus:ring-brand-100 accent-brand-500"
                />
                <span className="text-sm text-slate-700">{report.title}</span>
                {report.parsed_result?.rating && (
                  <span className="ml-2 text-xs text-slate-400">({report.parsed_result.rating})</span>
                )}
              </label>
            ))}
          </div>
        )}
        <div className="flex space-x-3 mt-4">
          <button
            onClick={handleCompare}
            disabled={selectedIds.length < 2 || isComparing}
            className="btn-primary disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 disabled:shadow-none disabled:cursor-not-allowed"
          >
            {isComparing ? '对比中...' : '开始对比'}
          </button>
          {compareResult && (
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-emerald-500 text-white text-sm rounded-lg hover:bg-emerald-600 transition-colors font-medium"
            >
              导出 CSV
            </button>
          )}
        </div>
      </div>

      {/* 对比结果 - 加载态 */}
      {isComparing && (
        <div className="glass-card p-6 animate-pulse">
          <div className="h-4 bg-brand-200 rounded w-1/4 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3].map(i => <div key={i} className="h-10 bg-brand-100 rounded" />)}
          </div>
        </div>
      )}

      {/* 对比结果 - 表格 */}
      {compareResult && !isComparing && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">研报</th>
                  {compareResult.headers.map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {compareResult.rows.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-slate-700">{row.report_id?.slice(0, 8)}...</td>
                    {compareResult.headers.map(h => (
                      <td key={h} className="px-4 py-3 text-sm text-slate-600">
                        {Array.isArray(row[h]) ? row[h].join('；') : (row[h] || '-')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default CompareTab
