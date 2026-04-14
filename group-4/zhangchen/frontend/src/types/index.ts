// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  nickname?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile extends User {
  total_contests: number;
  active_contests: number;
  total_return: number;
}

// 基金类型
export interface Fund {
  id: number;
  code: string;
  name: string;
  type?: string;
  company?: string;
  description?: string;
  risk_level?: number;
  created_at: string;
}

export interface FundWithPrice extends Fund {
  latest_nav?: number;
  latest_date?: string;
  daily_change?: number;
  daily_change_rate?: number;
}

export interface FundPrice {
  id: number;
  fund_id: number;
  nav: number;
  accum_nav?: number;
  date: string;
  created_at: string;
}

// 比赛类型
export interface Contest {
  id: number;
  name: string;
  description?: string;
  initial_balance: number;
  start_date: string;
  end_date: string;
  status: 'pending' | 'active' | 'ended';
  rules?: string;
  created_by?: number;
  created_at: string;
}

export interface ContestDetail extends Contest {
  participant_count: number;
  is_participating: boolean;
  my_rank?: number;
}

export interface ContestParticipant {
  id: number;
  contest_id: number;
  user_id: number;
  current_balance: number;
  total_assets: number;
  total_return: number;
  rank?: number;
  joined_at: string;
}

export interface ContestParticipantWithUser extends ContestParticipant {
  username: string;
  nickname?: string;
}

// 订单类型
export interface Order {
  id: number;
  user_id: number;
  contest_id: number;
  fund_id: number;
  order_type: 'buy' | 'sell';
  amount?: number;
  shares?: number;
  nav?: number;
  status: 'pending' | 'completed' | 'cancelled';
  created_at: string;
  executed_at?: string;
}

export interface OrderWithFund extends Order {
  fund_name: string;
  fund_code: string;
}

// 持仓类型
export interface Holding {
  id: number;
  user_id: number;
  contest_id: number;
  fund_id: number;
  shares: number;
  avg_cost: number;
  current_nav?: number;
  market_value?: number;
  profit_loss?: number;
  return_rate?: number;
  updated_at: string;
}

export interface HoldingWithFund extends Holding {
  fund_name: string;
  fund_code: string;
  fund_type?: string;
}

// 交易记录类型
export interface Transaction {
  id: number;
  user_id: number;
  contest_id: number;
  fund_id: number;
  transaction_type: 'buy' | 'sell';
  shares: number;
  nav: number;
  amount: number;
  fee: number;
  transaction_date: string;
}

export interface TransactionWithFund extends Transaction {
  fund_name: string;
  fund_code: string;
}

// 认证类型
export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  nickname?: string;
}

// API响应类型
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// 投资组合类型
export interface PortfolioOverview {
  contest_id: number;
  contest_name: string;
  cash_balance: number;
  market_value: number;
  total_assets: number;
  total_profit_loss: number;
  total_return_rate: number;
  rank?: number;
  holdings: HoldingItem[];
  holding_count: number;
}

export interface HoldingItem {
  fund_id: number;
  fund_code: string;
  fund_name: string;
  fund_type?: string;
  shares: number;
  avg_cost: number;
  current_nav: number;
  market_value: number;
  profit_loss: number;
  return_rate: number;
}

// 排行榜类型
export interface RankingItem {
  rank: number;
  user_id: number;
  username: string;
  nickname?: string;
  total_assets: number;
  total_return: number;
  is_me?: boolean;
}
