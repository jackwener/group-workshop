'use client';

import { useCallback } from 'react';
import { useChatStore } from '@/store/chatStore';
import { messageApi } from '@/lib/messageApi';
import { Message } from '@/types';

// SSE 事件类型
interface SSEEvent {
  event: string;
  data: string;
}

// SSE 数据类型
interface MessageStartData {
  message_id: number;
  model: string;
  provider?: string;
}

interface ContentBlockDeltaData {
  delta: {
    text: string;
  };
}

interface MessageStopData {
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  latency_ms?: number;
}

export function useChat(sessionId: number) {
  const {
    messages,
    isLoading,
    error,
    setMessages,
    addMessage,
    updateLastMessage,
    setLoading,
    setError,
    setCurrentSession,
  } = useChatStore();

  // 解析 SSE 行
  const parseSSELine = (line: string): { type: 'event' | 'data'; value: string } | null => {
    if (line.startsWith('event:')) {
      return { type: 'event', value: line.slice(6).trim() };
    }
    if (line.startsWith('data:')) {
      return { type: 'data', value: line.slice(5).trim() };
    }
    return null;
  };

  // 解析 SSE 流
  const parseSSEStream = async (reader: ReadableStreamDefaultReader<Uint8Array>) => {
    const decoder = new TextDecoder();
    let buffer = '';
    let currentEvent: SSEEvent | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;

        const parsed = parseSSELine(line);
        if (!parsed) continue;

        if (parsed.type === 'event') {
          currentEvent = { event: parsed.value, data: '' };
        } else if (parsed.type === 'data' && currentEvent) {
          currentEvent.data = parsed.value;

          // 处理完整事件
          await handleSSEEvent(currentEvent);
          currentEvent = null;
        }
      }
    }
  };

  // 处理 SSE 事件
  const handleSSEEvent = async (event: SSEEvent) => {
    try {
      switch (event.event) {
        case 'message_start': {
          const data: MessageStartData = JSON.parse(event.data);
          // 更新最后一条消息的 id 和 model 信息
          const store = useChatStore.getState();
          const lastMessage = store.messages[store.messages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            const updatedMessages = [...store.messages];
            updatedMessages[updatedMessages.length - 1] = {
              ...lastMessage,
              id: data.message_id,
              model: data.model,
              provider: data.provider,
            };
            setMessages(updatedMessages);
          }
          break;
        }

        case 'content_block_delta': {
          const data: ContentBlockDeltaData = JSON.parse(event.data);
          if (data.delta?.text) {
            updateLastMessage(data.delta.text);
          }
          break;
        }

        case 'message_stop': {
          const data: MessageStopData = JSON.parse(event.data);
          // 更新最后一条消息的 latency 信息
          const store = useChatStore.getState();
          const lastMessage = store.messages[store.messages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            const updatedMessages = [...store.messages];
            updatedMessages[updatedMessages.length - 1] = {
              ...lastMessage,
              latency_ms: data.latency_ms,
            };
            setMessages(updatedMessages);
          }
          break;
        }

        default:
          // 忽略其他事件
          break;
      }
    } catch (e) {
      console.error('Failed to parse SSE event:', event, e);
    }
  };

  // 加载历史消息
  const fetchMessages = useCallback(async (page = 1, pageSize = 50) => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);
    setCurrentSession(sessionId);

    try {
      const response = await messageApi.getMessages(sessionId, page, pageSize);
      setMessages(response.data.messages);
      return response.data.messages;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取消息失败';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId, setMessages, setLoading, setError, setCurrentSession]);

  // 发送消息（支持流式响应）
  const sendMessage = useCallback(async (content: string) => {
    if (!sessionId || !content.trim() || isLoading) return;

    setLoading(true);
    setError(null);

    // 1. 立即添加用户消息（乐观更新）
    const userMessage: Message = {
      id: Date.now(),
      session_id: sessionId,
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    };
    addMessage(userMessage);

    // 2. 添加空的 assistant 消息（用于流式填充）
    const assistantMessage: Message = {
      id: 0, // 将在 message_start 事件中更新
      session_id: sessionId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };
    addMessage(assistantMessage);

    try {
      // 3. 发起流式请求
      const response = await messageApi.sendMessage(sessionId, content.trim());

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      // 4. 读取 SSE 响应流
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      await parseSSEStream(reader);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '发送消息失败';
      setError(errorMessage);

      // 移除空的 assistant 消息
      const store = useChatStore.getState();
      const lastMessage = store.messages[store.messages.length - 1];
      if (lastMessage && lastMessage.role === 'assistant' && !lastMessage.content) {
        setMessages(store.messages.slice(0, -1));
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId, isLoading, addMessage, setMessages, setLoading, setError]);

  // 清除消息
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, [setMessages]);

  return {
    messages,
    isLoading,
    error,
    fetchMessages,
    sendMessage,
    clearMessages,
  };
}
