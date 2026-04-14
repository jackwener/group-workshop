const BASE = '/api/v1/agent'

// ========== Sessions (S1: T-013) ==========

export const getSessions = () =>
  fetch(`${BASE}/sessions`).then(r => r.json())

export const createSession = (title) =>
  fetch(`${BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  }).then(r => r.json())

export const deleteSession = (id) =>
  fetch(`${BASE}/sessions/${id}`, { method: 'DELETE' }).then(r => r.json())

// ========== QA (S2: T-027) ==========

export const askQuestion = (query, session_id) =>
  fetch(`${BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id }),
  }).then(r => r.json())

export const getRecords = (session_id) =>
  fetch(`${BASE}/sessions/${session_id}/records`).then(r => r.json())

// ========== Capabilities (S3: T-030) ==========

export const getCapabilities = () =>
  fetch(`${BASE}/capabilities`).then(r => r.json())
