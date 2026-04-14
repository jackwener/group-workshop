'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/types';
import { StreamingMessage } from './StreamingMessage';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

// 简单的 Markdown 转换函数
function simpleMarkdown(text: string): string {
  let result = text;

  // 代码块 ```code```
  result = result.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre class="bg-gray-800 text-gray-100 rounded-lg p-3 my-2 overflow-x-auto text-xs"><code>$2</code></pre>');

  // 行内代码 `code`
  result = result.replace(/`([^`]+)`/g, '<code class="bg-gray-100 text-pink-600 px-1.5 py-0.5 rounded text-xs">$1</code>');

  // 加粗 **text**
  result = result.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold">$1</strong>');

  // 斜体 *text*
  result = result.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // 无序列表
  result = result.replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>');

  // 有序列表
  result = result.replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal">$1</li>');

  // 换行
  result = result.replace(/\n/g, '<br />');

  return result;
}

// 格式化时间
function formatTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// 用户消息组件
function UserMessage({ message }: { message: Message }) {
  return (
    <div className="flex gap-3 justify-end">
      {/* 消息内容 */}
      <div className="flex-1 flex justify-end">
        <div className="max-w-[80%]">
          <div className="flex items-center justify-end gap-2 mb-1">
            <span className="text-xs text-gray-500">{formatTime(message.created_at)}</span>
            <span className="text-sm font-medium text-gray-900">我</span>
          </div>
          <div className="bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm">
            <div className="text-sm whitespace-pre-wrap break-words">
              {message.content}
            </div>
          </div>
        </div>
      </div>

      {/* 用户头像 */}
      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
        U
      </div>
    </div>
  );
}

// AI 消息组件
function AIMessage({ message, isStreaming }: { message: Message; isStreaming: boolean }) {
  // 如果是正在流式传输中且内容为空，显示思考中动画
  if (isStreaming && !message.content) {
    return (
      <div className="flex gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center text-white text-sm font-medium">
          A
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-gray-900">AI 助手</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>思考中...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 如果是流式传输中且有内容，显示流式消息
  if (isStreaming) {
    return (
      <StreamingMessage
        content={message.content}
        model={message.model}
        provider={message.provider}
      />
    );
  }

  // 完成的消息
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
          {message.model && (
            <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">
              {message.model}
            </span>
          )}
          {message.provider && (
            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
              {message.provider}
            </span>
          )}
          {message.latency_ms && (
            <span className="text-xs text-gray-400">
              {message.latency_ms}ms
            </span>
          )}
          <span className="text-xs text-gray-400">{formatTime(message.created_at)}</span>
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <div
            className="text-sm text-gray-900 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: simpleMarkdown(message.content) }}
          />
        </div>
      </div>
    </div>
  );
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // 空状态
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <p className="text-gray-500 text-sm">发送消息开始对话</p>
          <p className="text-gray-400 text-xs mt-1">按 Enter 快速发送</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="flex-1 overflow-auto px-4 py-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((message, index) => {
          const isLastMessage = index === messages.length - 1;
          const isStreaming = isLastMessage && isLoading && message.role === 'assistant';

          return (
            <div key={`${message.id}-${index}`}>
              {message.role === 'user' ? (
                <UserMessage message={message} />
              ) : (
                <AIMessage message={message} isStreaming={isStreaming} />
              )}
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
