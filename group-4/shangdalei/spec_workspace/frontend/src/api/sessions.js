/**
 * 会话管理API
 * 基于 05-用户故事与验收标准.md US-001
 */
import api from './index'

/**
 * 创建会话
 * AC-001-01: 用户可创建新会话
 */
export function createSession(name) {
  return api.post('/sessions', { name })
}

/**
 * 获取会话列表
 * AC-001-03: 用户可切换不同会话
 */
export function getSessions() {
  return api.get('/sessions')
}

/**
 * 删除会话
 * AC-001-02: 用户可删除会话
 */
export function deleteSession(sessionId) {
  return api.delete(`/sessions/${sessionId}`)
}
