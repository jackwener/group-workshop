import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as agentApi from '../api/agent'

export const useAgentStore = defineStore('agent', () => {
  // 状态（对齐文档 06 §7）
  const sessions = ref([])
  const currentSession = ref(null)
  const records = ref([])
  const loading = ref(false)
  const capabilities = ref(null)
  const error = ref(null)

  // 获取能力状态
  async function fetchCapabilities() {
    try {
      const { data } = await agentApi.getCapabilities()
      capabilities.value = data.providers
    } catch (e) {
      console.error('Failed to fetch capabilities', e)
    }
  }

  // 获取会话列表
  async function fetchSessions() {
    try {
      const { data } = await agentApi.getSessions()
      sessions.value = data.sessions
    } catch (e) {
      error.value = '获取会话列表失败'
    }
  }

  // 新建会话
  async function newSession(title) {
    try {
      const { data } = await agentApi.createSession(title)
      sessions.value.unshift(data.session)
      currentSession.value = data.session
      records.value = []
      return data.session
    } catch (e) {
      error.value = '新建会话失败'
    }
  }

  // 选择会话
  async function selectSession(session) {
    currentSession.value = session
    await fetchRecords(session.session_id)
  }

  // 删除会话
  async function removeSession(sessionId) {
    try {
      await agentApi.deleteSession(sessionId)
      sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
      if (currentSession.value?.session_id === sessionId) {
        currentSession.value = null
        records.value = []
      }
    } catch (e) {
      error.value = '删除会话失败'
    }
  }

  // 获取问答记录
  async function fetchRecords(sessionId) {
    try {
      const { data } = await agentApi.getRecords(sessionId)
      records.value = data.records
    } catch (e) {
      error.value = '获取记录失败'
    }
  }

  // 提交问答
  async function ask(query) {
    if (!currentSession.value) return
    loading.value = true
    error.value = null
    try {
      const { data } = await agentApi.askQuestion(query, currentSession.value.session_id)
      // 追加到记录列表
      records.value.push({
        id: data.record_id,
        session_id: currentSession.value.session_id,
        query,
        answer: data.answer,
        llm_used: data.llm_used,
        model: data.model,
        response_time_ms: data.response_time_ms,
        answer_source: data.answer_source,
        created_at: new Date().toISOString()
      })
      // 更新会话的 query_count
      if (currentSession.value) {
        currentSession.value.query_count = (currentSession.value.query_count || 0) + 1
      }
      // 刷新会话列表以获取自动命名
      await fetchSessions()
      // 保持当前会话选中
      const updated = sessions.value.find(s => s.session_id === currentSession.value?.session_id)
      if (updated) currentSession.value = updated
      return data
    } catch (e) {
      if (e.response?.data?.error) {
        error.value = e.response.data.error.message
      } else {
        error.value = '提交问答失败'
      }
    } finally {
      loading.value = false
    }
  }

  return {
    sessions, currentSession, records, loading, capabilities, error,
    fetchCapabilities, fetchSessions, newSession, selectSession, removeSession, fetchRecords, ask
  }
})
