<template>
  <div class="chat-area" ref="chatRef">
    <!-- 空状态：无会话 -->
    <div v-if="!currentSession" class="empty-state">
      <el-empty description="请选择或新建一个会话开始对话" :image-size="120" />
    </div>

    <!-- 空状态：有会话但无记录 -->
    <div v-else-if="records.length === 0" class="empty-state">
      <el-empty description="暂无对话记录" :image-size="80">
        <template #description>
          <p>试试输入以下问题：</p>
        </template>
      </el-empty>
      <div class="suggestions">
        <el-button
          v-for="q in suggestions"
          :key="q"
          size="small"
          @click="$emit('suggest', q)"
        >
          {{ q }}
        </el-button>
      </div>
    </div>

    <!-- 对话历史 -->
    <div v-else class="records-list">
      <RecordCard v-for="record in records" :key="record.id" :record="record" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-indicator">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>AI 正在思考中...</span>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref, nextTick } from 'vue'
import { useAgentStore } from '../store/agent'
import RecordCard from './RecordCard.vue'

defineEmits(['suggest'])

const store = useAgentStore()
const currentSession = computed(() => store.currentSession)
const records = computed(() => store.records)
const loading = computed(() => store.loading)
const chatRef = ref(null)

const suggestions = [
  '最近有哪些新的行业研报？',
  '帮我分析一下贵州茅台的最新研报',
  '对比最近三个月的医药行业研报数据'
]

// 自动滚动到底部
watch(records, async () => {
  await nextTick()
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  }
}, { deep: true })
</script>

<style scoped>
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  justify-content: center;
}
.records-list {
  max-width: 800px;
  margin: 0 auto;
}
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #409eff;
  font-size: 14px;
}
</style>
