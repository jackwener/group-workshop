'use client';

import { useChatStore } from '@/store/chatStore';

export function Header() {
  const { sessions, currentSessionId } = useChatStore();
  
  const currentSession = sessions.find(s => s.id === currentSessionId);

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
      {/* Left: Session Title */}
      <div className="flex items-center">
        {currentSession ? (
          <h2 className="text-gray-900 font-medium truncate max-w-md">
            {currentSession.title}
          </h2>
        ) : (
          <span className="text-gray-400 text-sm">选择一个会话开始对话</span>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Reserved for future actions */}
      </div>
    </header>
  );
}
