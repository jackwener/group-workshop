'use client';

import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Message } from '@/types';

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (content: string) => void;
}

export function ChatContainer({ messages, isLoading, onSendMessage }: ChatContainerProps) {
  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* 消息列表区域 - 可滚动 */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* 输入框区域 - 固定底部 */}
      <MessageInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
}
