<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史记录 - {{ sessionName }}</span>
          <el-button text @click="goBack">返回问答</el-button>
        </div>
      </template>
      
      <el-table :data="records" v-loading="loading">
        <el-table-column prop="query" label="问题" min-width="200" />
        <el-table-column prop="answer" label="回答" min-width="300">
          <template #default="{ row }">
            <div class="answer-cell">{{ truncate(row.answer, 100) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="answer_source" label="来源" width="100">
          <template #default="{ row }">
            <el-tag :type="getSourceTag(row.answer_source)" size="small">
              {{ row.answer_source }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchRecords"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="dialogVisible" title="问答详情" width="600px">
      <div v-if="currentRecord">
        <p><strong>问题：</strong></p>
        <p>{{ currentRecord.query }}</p>
        <el-divider />
        <p><strong>回答：</strong></p>
        <p>{{ currentRecord.answer }}</p>
        <el-divider />
        <p><strong>来源：</strong> {{ currentRecord.answer_source }}</p>
        <p><strong>时间：</strong> {{ formatDate(currentRecord.created_at) }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores'
import { getHistory } from '@/api/qa'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const sessionId = computed(() => route.params.sessionId)
const sessionName = computed(() => sessionStore.currentSession?.name || '未知会话')

const records = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const currentRecord = ref(null)

onMounted(() => {
  fetchRecords()
})

async function fetchRecords() {
  loading.value = true
  try {
    const res = await getHistory(sessionId.value, page.value, pageSize.value)
    records.value = res.records
    total.value = res.total
  } catch (error) {
    console.error('获取历史失败:', error)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function truncate(text, length) {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

function getSourceTag(source) {
  if (source === 'openai') return 'success'
  if (source === 'demo') return 'warning'
  return 'info'
}

function viewDetail(record) {
  currentRecord.value = record
  dialogVisible.value = true
}

function goBack() {
  router.push(`/qa/${sessionId.value}`)
}
</script>

<style scoped>
.history-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.answer-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
