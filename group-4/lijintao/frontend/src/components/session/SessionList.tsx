'use client';

import { useChatStore } from '@/store/chatStore';
import { SessionItem } from './SessionItem';

export function SessionList() {
  const { sessions, isLoading } = useChatStore();

  if (isLoading && sessions.length === 0) {
    return (
      <div className="p-4">
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div 
              key={i} 
              className="h-12 bg-slate-800 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-slate-500 text-sm">暂无会话</p>
        <p className="text-slate-600 text-xs mt-1">点击上方按钮创建新会话</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto py-2">
      <div className="px-2 space-y-1">
        {sessions.map((session) => (
          <SessionItem key={session.id} session={session} />
        ))}
      </div>
    </div>
  );
}
