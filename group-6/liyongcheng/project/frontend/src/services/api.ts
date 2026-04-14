import type { ApiResponse, ApiError, Report, PaginatedData, ComparisonData, StockPrice, Filters } from '../types';

const API_BASE = '/api/v1/research';

// 统一请求处理
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    const error = data as ApiError;
    throw new Error(error.error?.message || '请求失败');
  }

  return (data as ApiResponse<T>).data;
}

// ==================== 研报管理 ====================

/** 上传研报 */
export async function uploadReport(file: File): Promise<Report> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    const error = data as ApiError;
    throw new Error(error.error?.message || '上传失败');
  }

  return data.data;
}

/** 获取研报列表 */
export async function getReports(filters?: Filters): Promise<PaginatedData<Report>> {
  const params = new URLSearchParams();
  if (filters?.page) params.set('page', String(filters.page));
  if (filters?.page_size) params.set('page_size', String(filters.page_size));
  if (filters?.subject_code) params.set('subject_code', filters.subject_code);
  if (filters?.author) params.set('author', filters.author);
  if (filters?.keyword) params.set('keyword', filters.keyword);

  const query = params.toString();
  return request<PaginatedData<Report>>(`${API_BASE}/reports${query ? `?${query}` : ''}`);
}

/** 获取研报详情 */
export async function getReport(id: string): Promise<Report> {
  return request<Report>(`${API_BASE}/reports/${id}`);
}

/** 删除研报 */
export async function deleteReport(id: string): Promise<{ deleted_id: string; message: string }> {
  return request(`${API_BASE}/reports/${id}`, { method: 'DELETE' });
}

/** 研报对比 */
export async function compareReports(
  subjectCode: string,
  reportIds?: string[]
): Promise<ComparisonData> {
  return request<ComparisonData>(`${API_BASE}/reports/compare`, {
    method: 'POST',
    body: JSON.stringify({
      subject_code: subjectCode,
      report_ids: reportIds,
    }),
  });
}

// ==================== 股价查询 ====================

/** 获取股票价格 */
export async function getStockPrice(code: string): Promise<StockPrice> {
  return request<StockPrice>(`${API_BASE}/stock/price?code=${code}`);
}
