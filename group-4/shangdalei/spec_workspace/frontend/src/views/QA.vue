<template>
  <div class="qa-page">
    <el-row :gutter="20">
      <!-- 左侧：问答区域 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>问答 - {{ sessionName }}</span>
              <el-button text @click="goBack">返回会话列表</el-button>
            </div>
          </template>
          
          <!-- 问答输入 -->
          <div class="qa-input">
            <el-input
              v-model="query"
              type="textarea"
              :rows="3"
              placeholder="请输入您的问题（1-500字符）"
              :maxlength="500"
              show-word-limit
            />
            <el-button type="primary" :loading="loading" @click="submitQuery">
              提交问题
            </el-button>
          </div>
          
          <!-- 回答展示 -->
          <div v-if="answer" class="answer-section">
            <el-divider />
            <h4>回答</h4>
            <div class="answer-content">
              <el-tag :type="answerTag">{{ answerSource }}</el-tag>
              <p>{{ answer }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：历史记录 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>最近问答</span>
          </template>
          <div class="history-list">
            <div
              v-for="record in recentRecords"
              :key="record.created_at"
              class="history-item"
              @click="viewHistory"
            >
              <div class="query">{{ record.query }}</div>
              <div class="time">{{ formatDate(record.created_at) }}</div>
            </div>
            <el-empty v-if="recentRecords.length === 0" description="暂无问答记录" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { askQuestion, getHistory } from '@/api/qa'
import { useSessionStore } from '@/stores'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const sessionId = computed(() => route.params.sessionId)
const sessionName = computed(() => sessionStore.currentSession?.name || '未知会话')

const query = ref('')
const answer = ref('')
const answerSource = ref('')
const loading = ref(false)
const recentRecords = ref([])

const answerTag = computed(() => {
  if (answerSource.value === 'openai') return 'success'
  if (answerSource.value === 'demo') return 'warning'
  return 'info'
})

onMounted(() => {
  fetchRecentHistory()
})

async function fetchRecentHistory() {
  try {
    const res = await getHistory(sessionId.value, 1, 5)
    recentRecords.value = res.records
  } catch (error) {
    console.error('获取历史失败:', error)
  }
}

async function submitQuery() {
  if (!query.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  
  loading.value = true
  try {
    const res = await askQuestion(sessionId.value, query.value)
    answer.value = res.answer
    answerSource.value = res.answer_source
    ElMessage.success('回答已生成')
    fetchRecentHistory()
    query.value = ''
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function goBack() {
  router.push('/sessions')
}

function viewHistory() {
  router.push(`/history/${sessionId.value}`)
}
</script>

<style scoped>
.qa-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.qa-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.answer-section {
  margin-top: 20px;
}
.answer-content {
  margin-top: 10px;
}
.answer-content p {
  margin-top: 10px;
  line-height: 1.6;
}
.history-list {
  max-height: 500px;
  overflow-y: auto;
}
.history-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}
.history-item:hover {
  background: #f5f5f5;
}
.history-item .query {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.history-item .time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
