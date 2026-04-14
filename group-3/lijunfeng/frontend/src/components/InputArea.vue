<template>
  <div class="input-area">
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="store.error = null"
      class="error-alert"
    />
    <div class="input-row">
      <el-input
        v-model="query"
        type="textarea"
        :rows="3"
        placeholder="输入您的问题，例如：帮我分析一下最新的医药行业研报..."
        :disabled="!currentSession || loading"
        @keydown.enter.ctrl="handleSend"
        maxlength="500"
        show-word-limit
      />
      <div class="input-actions">
        <el-button
          type="primary"
          :icon="Promotion"
          :loading="loading"
          :disabled="!currentSession || !query.trim()"
          @click="handleSend"
        >
          发送
        </el-button>
        <el-button
          :icon="Delete"
          :disabled="!query"
          @click="query = ''"
        >
          清空
        </el-button>
      </div>
    </div>
    <div class="input-hint" v-if="currentSession">
      Ctrl + Enter 发送 · 当前会话：{{ currentSession.title }}
    </div>
    <div class="input-hint" v-else>
      请先新建或选择一个会话
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Promotion, Delete } from '@element-plus/icons-vue'
import { useAgentStore } from '../store/agent'

const store = useAgentStore()
const currentSession = computed(() => store.currentSession)
const loading = computed(() => store.loading)
const error = computed(() => store.error)
const query = ref('')

const handleSend = async () => {
  const text = query.value.trim()
  if (!text || !currentSession.value || loading.value) return
  query.value = ''
  await store.ask(text)
}

// 接收建议问题
const setSuggestion = (text) => {
  query.value = text
}

defineExpose({ setSuggestion })
</script>

<style scoped>
.input-area {
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}
.error-alert {
  margin-bottom: 12px;
}
.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
.input-row .el-textarea {
  flex: 1;
}
.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
