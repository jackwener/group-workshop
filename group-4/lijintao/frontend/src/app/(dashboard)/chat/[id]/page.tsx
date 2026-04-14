'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useChat } from '@/hooks/useChat';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { useChatStore } from '@/store/chatStore';

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = Number(params.id);

  const { messages, isLoading, error, fetchMessages, sendMessage } = useChat(sessionId);
  const { setCurrentSession, sessions } = useChatStore();

  // 验证会话是否存在
  useEffect(() => {
    if (sessionId) {
      // 设置当前会话
      setCurrentSession(sessionId);

      // 检查会话是否存在于列表中
      const sessionExists = sessions.some(s => s.id === sessionId);
      if (sessions.length > 0 && !sessionExists) {
        // 如果会话不存在，重定向到首页
        router.push('/');
        return;
      }

      // 加载历史消息
      fetchMessages();
    }
  }, [sessionId, fetchMessages, setCurrentSession, sessions, router]);

  // 错误处理
  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <p className="text-red-600 text-sm font-medium">{error}</p>
          <button
            onClick={() => fetchMessages()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  // 无效的会话 ID
  if (!sessionId || isNaN(sessionId)) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-500 text-sm">无效的会话</p>
          <button
            onClick={() => router.push('/')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  return (
    <ChatContainer
      messages={messages}
      isLoading={isLoading}
      onSendMessage={sendMessage}
    />
  );
}
