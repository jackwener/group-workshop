'use client';

import { useEffect } from 'react';
import { SessionList } from '@/components/session/SessionList';
import { NewSessionButton } from '@/components/session/NewSessionButton';
import { useSessions } from '@/hooks/useSessions';

export function Sidebar() {
  const { fetchSessions } = useSessions();

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return (
    <aside className="w-[280px] bg-slate-900 flex flex-col h-full flex-shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-slate-800">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center">
            <svg 
              className="w-4 h-4 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" 
              />
            </svg>
          </div>
          <h1 className="text-white font-semibold text-lg">投研问答助手</h1>
        </div>

        {/* New Session Button */}
        <NewSessionButton />
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-hidden">
        <SessionList />
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>系统运行正常</span>
        </div>
      </div>
    </aside>
  );
}
