function ChatArea({ currentSession, qaRecords, isLoading, onQuickQuestion }) {
  const defaultQuestions = [
    '最新的投资评级是什么？',
    '目标价是多少？',
    '核心观点有哪些？',
    '研报的数据预测如何？',
  ]

  const getSourceBadge = (record) => {
    const { answer_source } = record
    if (answer_source === 'copaw') {
      return <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200">CoPaw</span>
    }
    if (answer_source === 'bailian') {
      return <span className="badge bg-blue-50 text-blue-700 border border-blue-200">百炼</span>
    }
    return <span className="badge bg-slate-100 text-slate-500 border border-slate-200">Demo</span>
  }

  const getModelInfo = (record) => {
    const { answer_source, model } = record
    const sourceMap = { 'copaw': 'CoPaw', 'bailian': '百炼', 'demo': 'Demo' }
    return { sourceLabel: sourceMap[answer_source] || '未知', modelLabel: model || '-' }
  }

  if (!currentSession) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-slate-50 to-slate-100/50">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-brand-100 to-brand-200 flex items-center justify-center">
            <svg className="w-8 h-8 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
          </div>
          <p className="text-slate-400 font-medium">请创建或选择一个会话开始</p>
          <p className="text-xs text-slate-300 mt-1">在左侧点击「新建会话」开始分析</p>
        </div>
      </div>
    )
  }

  if (qaRecords.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 bg-gradient-to-b from-slate-50 to-slate-100/50">
        <div className="max-w-lg w-full">
          <p className="text-center text-slate-400 mb-6 font-medium">试试问一些问题</p>
          <div className="grid grid-cols-2 gap-3">
            {defaultQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => onQuickQuestion(q)}
                className="group p-4 text-sm text-left text-slate-600 glass-card hover:border-brand-300 hover:shadow-glow transition-all duration-200"
              >
                <span className="text-brand-500 mr-2 opacity-60 group-hover:opacity-100 transition-opacity">→</span>
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-slate-50 to-slate-100/50">
      {qaRecords.map((record) => (
        <div key={record.id} className="space-y-3">
          {/* 用户问题 */}
          <div className="flex justify-end">
            <div className="max-w-[70%] bg-gradient-to-br from-navy-800 to-navy-900 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-md">
              <p className="text-sm leading-relaxed">{record.query}</p>
            </div>
          </div>
          {/* 系统回答 */}
          <div className="flex justify-start">
            <div className="max-w-[70%] bg-white rounded-2xl rounded-tl-sm px-5 py-4 shadow-card border border-slate-100">
              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{record.answer}</p>
              <div className="mt-3 pt-3 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getSourceBadge(record)}
                    {(() => {
                      const { sourceLabel, modelLabel } = getModelInfo(record)
                      return (
                        <span className="text-[11px] text-slate-400 font-mono">
                          {sourceLabel} · {modelLabel}
                        </span>
                      )
                    })()}
                  </div>
                  <span className="text-[11px] text-slate-300 font-mono">{record.response_time_ms}ms</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-white rounded-2xl rounded-tl-sm px-5 py-4 shadow-card border border-slate-100">
            <div className="flex space-x-1.5">
              <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
              <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatArea
