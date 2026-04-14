const API_BASE_URL = '/api/v1/agent';

/**
 * HTTP客户端封装
 * 统一错误处理，traceId透传
 */
class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * 发送HTTP请求
   */
  async request(url, options = {}) {
    const fullUrl = `${this.baseURL}${url}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(fullUrl, config);
      const data = await response.json();

      if (!response.ok) {
        // 处理错误响应
        const error = data.error || { code: 'UNKNOWN_ERROR', message: '未知错误' };
        throw new ApiError(error.code, error.message, error.details, response.status);
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      // 网络错误等
      throw new ApiError('NETWORK_ERROR', error.message || '网络请求失败', null, 0);
    }
  }

  /**
   * GET请求
   */
  get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request(fullUrl, { method: 'GET' });
  }

  /**
   * POST请求
   */
  post(url, body = {}) {
    return this.request(url, { method: 'POST', body });
  }

  /**
   * DELETE请求
   */
  delete(url) {
    return this.request(url, { method: 'DELETE' });
  }
}

/**
 * API错误类
 */
class ApiError extends Error {
  constructor(code, message, details = null, status = 0) {
    super(message);
    this.code = code;
    this.details = details;
    this.status = status;
  }
}

// 创建API客户端实例
const client = new ApiClient();

/**
 * 能力探测API
 */
export const capabilitiesApi = {
  get: () => client.get('/capabilities'),
};

/**
 * 会话管理API
 */
export const sessionsApi = {
  create: (title) => client.post('/sessions', { title }),
  list: (page = 1, pageSize = 20) => client.get('/sessions', { page, page_size: pageSize }),
  delete: (sessionId) => client.delete(`/sessions/${sessionId}`),
  getRecords: (sessionId, page = 1, pageSize = 20) => 
    client.get(`/sessions/${sessionId}/records`, { page, page_size: pageSize }),
};

/**
 * 问答API
 */
export const qaApi = {
  ask: (sessionId, query) => client.post('/ask', { session_id: sessionId, query }),
};

/**
 * 研报管理API
 */
export const reportsApi = {
  upload: (file, title) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) {
      formData.append('title', title);
    }
    
    return fetch(`${API_BASE_URL}/reports`, {
      method: 'POST',
      body: formData,
    }).then(async (response) => {
      const data = await response.json();
      if (!response.ok) {
        const error = data.error || { code: 'UNKNOWN_ERROR', message: '未知错误' };
        throw new ApiError(error.code, error.message, error.details, response.status);
      }
      return data;
    });
  },
  list: (page = 1, pageSize = 20, status = null) => {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    return client.get('/reports', params);
  },
  delete: (reportId) => client.delete(`/reports/${reportId}`),
  analyze: (reportId) => client.post(`/reports/${reportId}/analyze`),
};

/**
 * 健康检查API
 */
export const healthApi = {
  check: () => client.get('/health'),
};

/**
 * 导出API
 */
export const exportApi = {
  export: (reportIds, format, company) => 
    client.post('/export', { report_ids: reportIds, format, company }),
};

export { ApiError };
export default client;
