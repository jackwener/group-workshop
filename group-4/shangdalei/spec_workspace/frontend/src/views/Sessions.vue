<template>
  <div class="sessions-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>会话管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建会话
          </el-button>
        </div>
      </template>
      
      <el-table :data="sessionStore.sessions" v-loading="sessionStore.loading">
        <el-table-column prop="name" label="会话名称" />
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="enterQA(row)">
              进入问答
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建会话对话框 -->
    <el-dialog v-model="dialogVisible" title="新建会话" width="400px">
      <el-form :model="form">
        <el-form-item label="会话名称">
          <el-input v-model="form.name" placeholder="请输入会话名称（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useSessionStore } from '@/stores'

const router = useRouter()
const sessionStore = useSessionStore()

const dialogVisible = ref(false)
const form = ref({ name: '' })

onMounted(() => {
  sessionStore.fetchSessions()
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function handleCreate() {
  form.value.name = ''
  dialogVisible.value = true
}

async function submitCreate() {
  try {
    await sessionStore.addSession(form.value.name || null)
    dialogVisible.value = false
    ElMessage.success('会话创建成功')
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

function enterQA(session) {
  sessionStore.setCurrentSession(session)
  router.push(`/qa/${session.session_id}`)
}

async function handleDelete(session) {
  try {
    await ElMessageBox.confirm('确定删除该会话？相关问答记录也将被删除。', '提示', {
      type: 'warning'
    })
    await sessionStore.removeSession(session.session_id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.sessions-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
