// 研报类型
export interface Report {
  id: string;
  title: string;
  subject_name: string;
  subject_code: string;
  author: string;
  rating: string;
  trend: 'bullish' | 'bearish' | 'neutral';
  target_price: number | null;
  summary: string;
  file_path: string;
  created_at: string;
  updated_at: string;
  parse_status: 'success' | 'partial' | 'failed';
}

// 股价类型
export interface StockPrice {
  code: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  amount: number;
  timestamp: string;
  source: string;
}

// API响应类型
export interface ApiResponse<T> {
  traceId: string;
  success: boolean;
  data: T;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
    traceId: string;
  };
}

// 分页数据
export interface PaginatedData<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

// 对比数据
export interface ComparisonItem {
  report_id: string;
  author: string;
  rating: string;
  trend: string;
  target_price: number | null;
  summary: string;
  publish_date: string;
}

export interface ComparisonData {
  subject_name: string;
  subject_code: string;
  report_count: number;
  comparison: ComparisonItem[];
}

// 筛选条件
export interface Filters {
  page?: number;
  page_size?: number;
  subject_code?: string;
  author?: string;
  keyword?: string;
}
