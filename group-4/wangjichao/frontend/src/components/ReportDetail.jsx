function ReportDetail({ report, onBack, onMark, onParse, onDelete }) {
  const parsed = report.parsed_result

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-slate-50 to-slate-100/50">
      {/* 顶部导航 */}
      <div className="flex items-center justify-between mb-6">
        <button onClick={onBack} className="text-sm text-slate-500 hover:text-slate-700 flex items-center space-x-1">
          ← 返回列表
        </button>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onMark(report.report_id, report.is_marked)}
            className="btn-secondary"
          >
            {report.is_marked ? '取消标记' : '标记重点'}
          </button>
          {report.status === 'pending' && (
            <button
              onClick={() => onParse(report.report_id)}
              className="btn-primary"
            >
              开始解析
            </button>
          )}
          <button
            onClick={() => onDelete(report.report_id)}
            className="btn-danger"
          >
            删除
          </button>
        </div>
      </div>

      {/* 基本信息 */}
      <div className="glass-card p-6 mb-6">
        <h2 className="text-lg font-bold text-slate-800 mb-4">{report.title}</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-slate-400">文件类型：</span>{report.file_type?.toUpperCase()}</div>
          <div><span className="text-slate-400">文件大小：</span>{(report.file_size / 1024).toFixed(1)} KB</div>
          <div><span className="text-slate-400">状态：</span>
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
              report.status === 'completed' ? 'bg-green-100 text-green-800' :
              report.status === 'failed' ? 'bg-red-100 text-red-800' :
              report.status === 'parsing' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>{report.status}</span>
          </div>
          <div><span className="text-slate-400">上传时间：</span>{report.uploaded_at ? new Date(report.uploaded_at).toLocaleString() : '-'}</div>
          {parsed?.rating && <div><span className="text-slate-400">评级：</span><span className="font-medium text-slate-700">{parsed.rating}</span></div>}
          {parsed?.target_price && <div><span className="text-slate-400">目标价：</span><span className="font-medium text-slate-700">{parsed.target_price}</span></div>}
        </div>
      </div>

      {/* 核心观点 */}
      {parsed?.core_views && parsed.core_views.length > 0 && (
        <div className="glass-card p-6 mb-6">
          <h3 className="text-md font-bold text-slate-800 mb-3">核心观点</h3>
          <ul className="space-y-2">
            {parsed.core_views.map((view, i) => (
              <li key={i} className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 bg-brand-100 text-brand-600 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-sm text-slate-600 leading-relaxed">{view}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 数据预测 */}
      {parsed?.data_forecast && Object.keys(parsed.data_forecast).length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-md font-bold text-slate-800 mb-3">数据预测</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(parsed.data_forecast).map(([key, value]) => (
              <div key={key} className="flex justify-between p-3 bg-slate-50 rounded-lg">
                <span className="text-slate-500">{key}</span>
                <span className="font-medium text-slate-700">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportDetail
