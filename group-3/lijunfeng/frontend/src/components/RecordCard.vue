<template>
  <div class="record-card" :class="sourceClass">
    <div class="record-query">
      <el-icon><User /></el-icon>
      <span>{{ record.query }}</span>
    </div>
    <div class="record-answer">
      <el-icon><ChatDotRound /></el-icon>
      <div class="answer-content">
        <pre class="answer-text">{{ record.answer }}</pre>
        <div class="answer-meta">
          <el-tag :type="sourceTagType" size="small" effect="plain">
            {{ sourceLabel }}
          </el-tag>
          <span class="meta-item">{{ record.model }}</span>
          <span class="meta-item">{{ record.response_time_ms }}ms</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  record: { type: Object, required: true }
})

const sourceLabel = computed(() => {
  const map = { copaw: 'CoPaw', bailian: '百炼', demo: '离线演示' }
  return map[props.record.answer_source] || props.record.answer_source
})

const sourceTagType = computed(() => {
  const map = { copaw: 'success', bailian: 'primary', demo: 'info' }
  return map[props.record.answer_source] || 'info'
})

const sourceClass = computed(() => `source-${props.record.answer_source}`)
</script>

<style scoped>
.record-card {
  margin-bottom: 16px;
  padding: 0;
}
.record-query {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  background: #f0f7ff;
  border-radius: 8px 8px 0 0;
  color: #303133;
  font-size: 14px;
}
.record-answer {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-top: none;
  border-radius: 0 0 8px 8px;
}
.answer-content {
  flex: 1;
  min-width: 0;
}
.answer-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}
.answer-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
.meta-item {
  font-size: 12px;
  color: #909399;
}
.source-demo .record-answer {
  background: #fafafa;
}
</style>
