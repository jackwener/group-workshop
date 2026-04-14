import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  login: async (username, password) => {
    set({ loading: true, error: null });
    
    // 模拟 API 调用
    return new Promise((resolve) => {
      setTimeout(() => {
        // 模拟验证：用户名 admin，密码 123456
        if (username === 'admin' && password === '123456') {
          const user = { username, name: '管理员' };
          localStorage.setItem('user', JSON.stringify(user));
          set({ user, isAuthenticated: true, loading: false, error: null });
          resolve({ success: true });
        } else {
          set({ loading: false, error: '用户名或密码错误' });
          resolve({ success: false, error: '用户名或密码错误' });
        }
      }, 800);
    });
  },

  logout: () => {
    localStorage.removeItem('user');
    set({ user: null, isAuthenticated: false, error: null });
  },

  // 初始化时检查本地存储
  initialize: () => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      set({ user: JSON.parse(storedUser), isAuthenticated: true });
    }
  },
}));

export default useAuthStore;
