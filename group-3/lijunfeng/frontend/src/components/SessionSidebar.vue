<template>
  <div class="session-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">会话列表</span>
      <el-button type="primary" size="small" @click="handleNew" :icon="Plus">
        新建
      </el-button>
    </div>
    <el-scrollbar class="session-list">
      <div
        v-for="session in sessions"
        :key="session.session_id"
        class="session-item"
        :class="{ active: currentSession?.session_id === session.session_id }"
        @click="handleSelect(session)"
      >
        <div class="session-info">
          <span class="session-title">{{ session.title }}</span>
          <span class="session-count">{{ session.query_count || 0 }} 条问答</span>
        </div>
        <el-button
          type="danger"
          size="small"
          text
          :icon="Delete"
          @click.stop="handleDelete(session.session_id)"
        />
      </div>
      <el-empty v-if="sessions.length === 0" description="暂无会话" :image-size="60" />
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { useAgentStore } from '../store/agent'
import { ElMessageBox } from 'element-plus'

const store = useAgentStore()
const sessions = computed(() => store.sessions)
const currentSession = computed(() => store.currentSession)

const handleNew = () => store.newSession()
const handleSelect = (session) => store.selectSession(session)
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该会话及其所有记录？', '删除确认', {
      type: 'warning'
    })
    await store.removeSession(id)
  } catch {
    // 取消
  }
}

onMounted(() => {
  store.fetchSessions()
})
</script>

<style scoped>
.session-sidebar {
  width: 260px;
  min-width: 260px;
  background: #fafafa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}
.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
.session-list {
  flex: 1;
  overflow: auto;
}
.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}
.session-item:hover {
  background: #ecf5ff;
}
.session-item.active {
  background: #e1eeff;
  border-left: 3px solid #409eff;
}
.session-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}
.session-title {
  font-size: 13px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.session-count {
  font-size: 11px;
  color: #909399;
}
</style>
