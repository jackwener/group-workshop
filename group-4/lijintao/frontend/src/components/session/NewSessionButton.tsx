'use client';

import { useRouter } from 'next/navigation';
import { useSessions } from '@/hooks/useSessions';
import { useChatStore } from '@/store/chatStore';

export function NewSessionButton() {
  const router = useRouter();
  const { createSession } = useSessions();
  const { isLoading } = useChatStore();

  const handleClick = async () => {
    if (isLoading) return;
    
    try {
      const newSession = await createSession();
      router.push(`/chat/${newSession.id}`);
    } catch (error) {
      console.error('创建会话失败:', error);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className="
        w-full flex items-center justify-center gap-2 
        px-4 py-2.5 
        bg-blue-600 hover:bg-blue-700 
        disabled:bg-blue-800 disabled:cursor-not-allowed
        text-white font-medium text-sm
        rounded-lg 
        transition-all duration-200
        shadow-sm hover:shadow-md
      "
    >
      <svg 
        className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        {isLoading ? (
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
          />
        ) : (
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M12 4v16m8-8H4" 
          />
        )}
      </svg>
      新建会话
    </button>
  );
}
