import { create } from 'zustand';
import { Session, Message } from '@/types';

interface ChatState {
  sessions: Session[];
  currentSessionId: number | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setSessions: (sessions: Session[]) => void;
  setCurrentSession: (id: number | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addSession: (session: Session) => void;
  removeSession: (id: number) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  sessions: [],
  currentSessionId: null,
  messages: [],
  isLoading: false,
  error: null,

  setSessions: (sessions) => set({ sessions }),
  
  setCurrentSession: (id) => set({ currentSessionId: id }),
  
  setMessages: (messages) => set({ messages }),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  
  updateLastMessage: (content) => set((state) => {
    if (state.messages.length === 0) return state;
    const lastIndex = state.messages.length - 1;
    const updatedMessages = [...state.messages];
    updatedMessages[lastIndex] = {
      ...updatedMessages[lastIndex],
      content: updatedMessages[lastIndex].content + content,
    };
    return { messages: updatedMessages };
  }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions],
  })),
  
  removeSession: (id) => set((state) => ({
    sessions: state.sessions.filter((s) => s.id !== id),
    currentSessionId: state.currentSessionId === id ? null : state.currentSessionId,
  })),
}));
