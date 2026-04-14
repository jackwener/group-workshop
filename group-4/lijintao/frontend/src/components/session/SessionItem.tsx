'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Session } from '@/types';
import { useChatStore } from '@/store/chatStore';
import { useSessions } from '@/hooks/useSessions';

interface SessionItemProps {
  session: Session;
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) {
    return '刚刚';
  } else if (diffMins < 60) {
    return `${diffMins}分钟前`;
  } else if (diffHours < 24) {
    return `${diffHours}小时前`;
  } else if (diffDays < 7) {
    return `${diffDays}天前`;
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  }
}

export function SessionItem({ session }: SessionItemProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { setCurrentSession, currentSessionId } = useChatStore();
  const { deleteSession } = useSessions();
  const [isHovered, setIsHovered] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const isActive = currentSessionId === session.id || pathname === `/chat/${session.id}`;

  const handleClick = () => {
    setCurrentSession(session.id);
    router.push(`/chat/${session.id}`);
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isDeleting) return;
    
    setIsDeleting(true);
    try {
      await deleteSession(session.id);
      if (isActive) {
        router.push('/');
      }
    } catch (error) {
      console.error('删除会话失败:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        group relative flex items-center gap-3 px-3 py-3 rounded-lg cursor-pointer
        transition-all duration-200
        ${isActive 
          ? 'bg-blue-600 hover:bg-blue-700' 
          : 'hover:bg-slate-800'
        }
      `}
    >
      {/* Chat Icon */}
      <div className={`
        flex-shrink-0 w-8 h-8 rounded-md flex items-center justify-center
        ${isActive ? 'bg-blue-500' : 'bg-slate-800 group-hover:bg-slate-700'}
      `}>
        <svg 
          className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
          />
        </svg>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className={`
          text-sm font-medium truncate
          ${isActive ? 'text-white' : 'text-slate-200'}
        `}>
          {session.title}
        </p>
        <p className={`
          text-xs mt-0.5
          ${isActive ? 'text-blue-200' : 'text-slate-500'}
        `}>
          {formatRelativeTime(session.updated_at)}
        </p>
      </div>

      {/* Delete Button */}
      {(isHovered || isActive) && (
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className={`
            flex-shrink-0 p-1.5 rounded-md transition-colors
            ${isActive 
              ? 'hover:bg-blue-500 text-blue-200 hover:text-white' 
              : 'hover:bg-slate-700 text-slate-500 hover:text-red-400'
            }
            ${isDeleting ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          title="删除会话"
        >
          <svg 
            className="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" 
            />
          </svg>
        </button>
      )}
    </div>
  );
}
