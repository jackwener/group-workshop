/**
 * API 客户端
 * 对齐 09-API接口规格
 */

const API_BASE = 'http://localhost:5001/api/v1/agent';

/**
 * 生成 traceId（用于调试）
 */
function generateTraceId() {
  return `tr_${Math.random().toString(36).substring(2, 15)}`;
}

/**
 * 统一请求封装
 */
async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || '请求失败');
  }

  return data;
}

// ==================== 能力探测与健康检查 ====================

export async function getCapabilities() {
  return request(`${API_BASE}/capabilities`);
}

export async function healthCheck() {
  return request(`${API_BASE}/health`);
}

// ==================== 问答 API ====================

export async function ask(query, sessionId) {
  return request(`${API_BASE}/ask`, {
    method: 'POST',
    body: JSON.stringify({ query, session_id: sessionId }),
  });
}

// ==================== 会话管理 API ====================

export async function getSessions() {
  return request(`${API_BASE}/sessions`);
}

export async function createSession(title = '新会话') {
  return request(`${API_BASE}/sessions`, {
    method: 'POST',
    body: JSON.stringify({ title }),
  });
}

export async function deleteSession(sessionId) {
  return request(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
}

// ==================== 问答记录 API ====================

export async function getSessionRecords(sessionId) {
  return request(`${API_BASE}/sessions/${sessionId}/records`);
}
