import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1/agent',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 能力探测
export const getCapabilities = () => api.get('/capabilities')

// 问答提交
export const askQuestion = (query, sessionId) =>
  api.post('/ask', { query, session_id: sessionId })

// 会话列表
export const getSessions = () => api.get('/sessions')

// 新建会话
export const createSession = (title) =>
  api.post('/sessions', title ? { title } : {})

// 删除会话
export const deleteSession = (id) => api.delete(`/sessions/${id}`)

// 问答记录
export const getRecords = (sessionId) =>
  api.get(`/sessions/${sessionId}/records`)

export default api
