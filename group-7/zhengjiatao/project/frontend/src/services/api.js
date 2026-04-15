const API_BASE = '/api/v1/agent';

/**
 * 统一错误处理
 */
async function handleResponse(response) {
  const data = await response.json();
  
  if (!response.ok) {
    const error = new Error(data.error?.message || '请求失败');
    error.code = data.error?.code;
    error.details = data.error?.details;
    error.traceId = data.error?.traceId || data.traceId;
    throw error;
  }
  
  return data;
}

/**
 * 获取会话列表
 */
export async function getSessions() {
  const response = await fetch(`${API_BASE}/sessions`);
  return handleResponse(response);
}

/**
 * 创建新会话
 */
export async function createSession(title = '新会话') {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title }),
  });
  return handleResponse(response);
}

/**
 * 删除会话
 */
export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
}

/**
 * 获取会话的问答记录
 */
export async function getRecordsBySession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/records`);
  return handleResponse(response);
}

/**
 * 提交问答
 */
export async function ask(sessionId, query) {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ session_id: sessionId, query }),
  });
  return handleResponse(response);
}

/**
 * 导出会话记录
 */
export async function exportSession(sessionId, format = 'json') {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/export?format=${format}`);
  
  if (!response.ok) {
    const data = await response.json();
    const error = new Error(data.error?.message || '导出失败');
    error.code = data.error?.code;
    throw error;
  }
  
  // 获取文件名
  const contentDisposition = response.headers.get('content-disposition');
  let filename = `session_export.${format}`;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^"]+)"?/);
    if (match) {
      filename = match[1];
    }
  }
  
  // 下载文件
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
  
  return { success: true, filename };
}

/**
 * 获取系统能力状态
 */
export async function getCapabilities() {
  const response = await fetch(`${API_BASE}/capabilities`);
  return handleResponse(response);
}

/**
 * 获取系统健康状态
 */
export async function getSystemStatus() {
  const response = await fetch(`${API_BASE}/system-status`);
  return handleResponse(response);
}
