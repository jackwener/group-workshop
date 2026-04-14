import axios, { AxiosInstance, AxiosError } from 'axios';
import type { 
  User, UserProfile, LoginRequest, RegisterRequest, Token,
  Fund, FundWithPrice, FundPrice,
  Contest, ContestDetail, ContestParticipant, ContestParticipantWithUser,
  Order, OrderWithFund,
  Holding, HoldingWithFund,
  Transaction, TransactionWithFund,
  PortfolioOverview, RankingItem
} from '../types';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证API
export const authApi = {
  login: (data: LoginRequest) => api.post<Token>('/auth/login/json', data),
  register: (data: RegisterRequest) => api.post<User>('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get<User>('/auth/me'),
};

// 用户API
export const userApi = {
  getProfile: () => api.get<User>('/users/profile'),
  updateProfile: (data: Partial<User>) => api.put<User>('/users/profile', data),
  getStatistics: () => api.get<UserProfile>('/users/statistics'),
};

// 基金API
export const fundApi = {
  getFunds: (params?: { skip?: number; limit?: number; fund_type?: string; search?: string }) => 
    api.get<FundWithPrice[]>('/funds', { params }),
  getFund: (id: number) => api.get<FundWithPrice>(`/funds/${id}`),
  getFundPrices: (id: number, days?: number) => 
    api.get<FundPrice[]>(`/funds/${id}/prices`, { params: { days } }),
  getFundChart: (id: number, days?: number) => 
    api.get<{ dates: string[]; navs: number[]; accum_navs: number[] }>(`/funds/${id}/chart`, { params: { days } }),
  searchFunds: (q: string) => api.get<FundWithPrice[]>('/funds/search', { params: { q } }),
  getFundTypes: () => api.get<string[]>('/funds/types/list'),
};

// 比赛API
export const contestApi = {
  getContests: (params?: { skip?: number; limit?: number; status?: string }) => 
    api.get<Contest[]>('/contests', { params }),
  getContest: (id: number) => api.get<ContestDetail>(`/contests/${id}`),
  createContest: (data: Partial<Contest>) => api.post<Contest>('/contests', data),
  updateContest: (id: number, data: Partial<Contest>) => api.put<Contest>(`/contests/${id}`, data),
  deleteContest: (id: number) => api.delete(`/contests/${id}`),
  joinContest: (id: number) => api.post<ContestParticipant>(`/contests/${id}/join`),
  getParticipants: (id: number) => api.get<ContestParticipantWithUser[]>(`/contests/${id}/participants`),
  getMyContestData: (id: number) => api.get<ContestParticipant>(`/contests/${id}/me`),
};

// 交易API
export const tradeApi = {
  buyFund: (data: { contest_id: number; fund_id: number; amount: number }) => 
    api.post<Order>('/trade/buy', data),
  sellFund: (data: { contest_id: number; fund_id: number; shares: number }) => 
    api.post<Order>('/trade/sell', data),
  getOrders: (contestId?: number) => api.get<OrderWithFund[]>('/trade/orders', { params: { contest_id: contestId } }),
};

// 投资组合API
export const portfolioApi = {
  getOverview: (contestId: number) => api.get<PortfolioOverview>('/portfolio/overview', { params: { contest_id: contestId } }),
  getHoldings: (contestId: number) => api.get<HoldingWithFund[]>('/portfolio/holdings', { params: { contest_id: contestId } }),
  getProfitCurve: (contestId: number, days?: number) => 
    api.get('/portfolio/profit', { params: { contest_id: contestId, days } }),
  getDistribution: (contestId: number) => api.get('/portfolio/distribution', { params: { contest_id: contestId } }),
  getAnalysis: (contestId: number) => api.get('/portfolio/analysis', { params: { contest_id: contestId } }),
};

// 排行榜API
export const rankingApi = {
  getGlobalRankings: (params?: { skip?: number; limit?: number }) => 
    api.get<RankingItem[]>('/rankings', { params }),
  getContestRankings: (contestId: number) => api.get<{ rankings: RankingItem[]; my_rank?: number }>(`/rankings/${contestId}`),
  getDailyRankings: (contestId: number, date?: string) => 
    api.get(`/rankings/${contestId}/daily`, { params: { date } }),
  getWeeklyRankings: (contestId: number) => api.get(`/rankings/${contestId}/weekly`),
};

// 交易记录API
export const transactionApi = {
  getTransactions: (params?: { contest_id?: number; fund_id?: number; transaction_type?: string }) => 
    api.get<TransactionWithFund[]>('/transactions', { params }),
  getSummary: (contestId?: number) => api.get('/transactions/summary', { params: { contest_id: contestId } }),
  getRecent: (days?: number) => api.get('/transactions/recent', { params: { days } }),
};

export default api;
