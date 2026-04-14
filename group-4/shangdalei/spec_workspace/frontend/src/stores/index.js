/**
 * Pinia状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSessions, createSession, deleteSession } from '@/api/sessions'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref([])
  const currentSession = ref(null)
  const loading = ref(false)

  async function fetchSessions() {
    loading.value = true
    try {
      const res = await getSessions()
      sessions.value = res.sessions
    } catch (error) {
      console.error('获取会话列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function addSession(name) {
    try {
      const res = await createSession(name)
      sessions.value.unshift({
        session_id: res.session_id,
        name: res.name,
        created_at: res.created_at
      })
      return res
    } catch (error) {
      console.error('创建会话失败:', error)
      throw error
    }
  }

  async function removeSession(sessionId) {
    try {
      await deleteSession(sessionId)
      sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
      if (currentSession.value?.session_id === sessionId) {
        currentSession.value = null
      }
    } catch (error) {
      console.error('删除会话失败:', error)
      throw error
    }
  }

  function setCurrentSession(session) {
    currentSession.value = session
  }

  return {
    sessions,
    currentSession,
    loading,
    fetchSessions,
    addSession,
    removeSession,
    setCurrentSession
  }
})
