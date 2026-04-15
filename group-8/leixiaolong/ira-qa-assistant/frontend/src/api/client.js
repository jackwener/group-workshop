const BASE_URL = '/api/v1/agent';

class ApiError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    const err = data.error || {};
    throw new ApiError(
      err.code || 'UNKNOWN_ERROR',
      err.message || '请求失败',
      err.details || {}
    );
  }

  return data;
}

// ─── S1: Session APIs ──────────────────────────────────────

export async function getSessions() {
  return request('/sessions');
}

export async function createSession(title) {
  const body = title ? { title } : {};
  return request('/sessions', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function deleteSession(sessionId) {
  return request(`/sessions/${sessionId}`, {
    method: 'DELETE',
  });
}

// ─── S2: Q&A APIs ──────────────────────────────────────────

export async function getRecords(sessionId) {
  return request(`/sessions/${sessionId}/records`);
}

export async function submitQuestion(query, sessionId) {
  return request('/ask', {
    method: 'POST',
    body: JSON.stringify({ query, session_id: sessionId }),
  });
}

export { ApiError };
