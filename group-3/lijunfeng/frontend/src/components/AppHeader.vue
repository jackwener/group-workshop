<template>
  <div class="app-header">
    <div class="header-left">
      <el-icon :size="24"><DataAnalysis /></el-icon>
      <span class="header-title">投研AI研报解读助手</span>
      <el-tag size="small" type="info">M1-QA</el-tag>
    </div>
    <div class="header-right">
      <el-tag
        v-for="(info, name) in capabilities"
        :key="name"
        :type="info.available ? 'success' : 'danger'"
        size="small"
        class="cap-chip"
        effect="plain"
      >
        {{ chipLabel(name) }}：{{ info.available ? '可用' : '不可用' }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAgentStore } from '../store/agent'

const store = useAgentStore()
const capabilities = computed(() => store.capabilities || {})

const chipLabel = (name) => {
  const map = { copaw: 'CoPaw', bailian: '百炼', demo: 'Demo' }
  return map[name] || name
}

onMounted(() => {
  store.fetchCapabilities()
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.header-right {
  display: flex;
  gap: 8px;
}
.cap-chip {
  font-size: 12px;
}
</style>
