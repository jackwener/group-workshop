function InputArea({ inputValue, setInputValue, onSend, isLoading }) {
  const handleSubmit = () => {
    if (!inputValue.trim() || isLoading) return
    onSend(inputValue.trim())
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-slate-200 bg-white/80 backdrop-blur-sm p-4">
      <div className="flex space-x-3 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入您的问题... (Enter 发送，Shift+Enter 换行)"
            rows={2}
            className="w-full resize-none border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100 transition-all duration-200 bg-slate-50/50 placeholder:text-slate-300"
            disabled={isLoading}
          />
        </div>
        <div className="flex flex-col space-y-2">
          <button
            onClick={handleSubmit}
            disabled={isLoading || !inputValue.trim()}
            className="btn-primary disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 disabled:shadow-none disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center space-x-1">
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                <span>发送中</span>
              </span>
            ) : '发送'}
          </button>
          <button
            onClick={() => setInputValue('')}
            className="btn-secondary text-xs"
          >
            清空
          </button>
        </div>
      </div>
    </div>
  )
}

export default InputArea
