'use client';

interface StreamingMessageProps {
  content: string;
  model?: string;
  provider?: string;
}

export function StreamingMessage({ content, model, provider }: StreamingMessageProps) {
  return (
    <div className="flex gap-3">
      {/* AI 头像 */}
      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center text-white text-sm font-medium">
        A
      </div>

      {/* 消息内容 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-gray-900">AI 助手</span>
          {model && (
            <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">
              {model}
            </span>
          )}
          {provider && (
            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
              {provider}
            </span>
          )}
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <div className="text-sm text-gray-900 whitespace-pre-wrap break-words">
            {content}
            {/* 闪烁光标 */}
            <span className="inline-block w-0.5 h-4 bg-purple-600 ml-0.5 animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  );
}
