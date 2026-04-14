/**
 * 问答API
 * 基于 05-用户故事与验收标准.md US-002
 */
import api from './index'

/**
 * 提交问答
 * AC-002-01: 用户可提交问题并获取回答
 */
export function askQuestion(sessionId, query) {
  return api.post('/qa/ask', {
    session_id: sessionId,
    query: query
  })
}

/**
 * 获取问答历史
 * AC-002-02: 支持问答历史记录查看
 */
export function getHistory(sessionId, page = 1, pageSize = 20) {
  return api.get('/qa/history', {
    params: {
      session_id: sessionId,
      page,
      page_size: pageSize
    }
  })
}

/**
 * 重新发送问题
 * AC-002-03: 支持重新发送问题
 */
export function resendQuestion(recordId) {
  return api.post(`/qa/resend/${recordId}`)
}
