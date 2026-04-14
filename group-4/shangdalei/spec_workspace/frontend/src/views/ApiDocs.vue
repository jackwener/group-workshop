<template>
  <div class="api-docs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="title-area">
            <span class="title">API 接口文档</span>
            <el-tag v-if="apiInfo" type="success" size="small">{{ Object.keys(allApis).length }} 个接口</el-tag>
          </div>
          <el-button @click="fetchApiDocs" :loading="loading" size="small">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <!-- API 基本信息 -->
      <div v-if="apiInfo" class="api-info-bar">
        <el-tag>{{ apiInfo.info?.title }}</el-tag>
        <el-tag type="info">v{{ apiInfo.info?.version }}</el-tag>
        <el-tag type="warning">Base: http://localhost:8000</el-tag>
      </div>

      <el-empty v-if="!loading && !apiInfo" description="无法获取 API 文档，请确认后端已启动" />

      <!-- 分组接口列表 -->
      <div v-if="apiInfo" class="groups-container">
        <div v-for="(apis, tag) in groupedApis" :key="tag" class="group-block">
          <!-- 标签标题 -->
          <div class="group-header" @click="toggleGroup(tag)">
            <el-icon class="arrow" :class="{ open: openGroups.has(tag) }"><ArrowRight /></el-icon>
            <span class="group-name">{{ tag }}</span>
            <el-tag size="small" type="info">{{ apis.length }} 个</el-tag>
          </div>

          <!-- 接口列表 -->
          <div v-show="openGroups.has(tag)" class="api-list">
            <div
              v-for="api in apis"
              :key="`${api.method}-${api.path}`"
              class="api-item"
              :class="{ expanded: expandedApis.has(`${api.method}-${api.path}`) }"
            >
              <!-- 接口行 -->
              <div class="api-row" @click="toggleApi(api)">
                <el-tag :type="methodColor(api.method)" size="small" class="method-tag">
                  {{ api.method.toUpperCase() }}
                </el-tag>
                <span class="api-path">{{ api.path }}</span>
                <span class="api-summary">{{ api.summary }}</span>
                <el-icon class="arrow-small" :class="{ open: expandedApis.has(`${api.method}-${api.path}`) }">
                  <ArrowRight />
                </el-icon>
              </div>

              <!-- 展开详情 -->
              <div v-show="expandedApis.has(`${api.method}-${api.path}`)" class="api-detail">
                <p v-if="api.description" class="desc-text">{{ api.description }}</p>

                <!-- 路径/查询参数 -->
                <div v-if="api.parameters?.length" class="section">
                  <div class="section-title">请求参数</div>
                  <el-table :data="api.parameters" size="small" border>
                    <el-table-column prop="name" label="参数名" width="140" />
                    <el-table-column prop="in" label="位置" width="90" />
                    <el-table-column label="必填" width="70">
                      <template #default="{ row }">
                        <el-tag :type="row.required ? 'danger' : 'success'" size="small">
                          {{ row.required ? '是' : '否' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="type" label="类型" width="100" />
                    <el-table-column prop="description" label="说明" />
                  </el-table>
                </div>

                <!-- 请求体 -->
                <div v-if="api.requestSchema" class="section">
                  <div class="section-title">请求体 Schema</div>
                  <div class="schema-box">
                    <div v-for="(field, key) in api.requestSchema.properties" :key="key" class="schema-row">
                      <span class="field-name">{{ key }}</span>
                      <el-tag size="small" type="info">{{ getFieldType(field) }}</el-tag>
                      <el-tag v-if="api.requestSchema.required?.includes(key)" size="small" type="danger">必填</el-tag>
                      <span class="field-desc">{{ field.description || '' }}</span>
                    </div>
                  </div>
                </div>

                <!-- 响应 -->
                <div class="section">
                  <div class="section-title">响应说明</div>
                  <div v-for="(resp, code) in api.responses" :key="code" class="response-row">
                    <el-tag :type="codeColor(String(code))" size="small">{{ code }}</el-tag>
                    <span class="resp-desc">{{ resp.description }}</span>
                    <span v-if="getResponseSchema(resp)" class="resp-schema">
                      → {{ getResponseSchema(resp) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import axios from 'axios'

const apiInfo = ref(null)
const loading = ref(false)
const openGroups = reactive(new Set())
const expandedApis = reactive(new Set())

// 所有接口平铺列表（用于计数）
const allApis = computed(() => {
  const result = {}
  if (!apiInfo.value?.paths) return result
  for (const [path, methods] of Object.entries(apiInfo.value.paths)) {
    for (const [method] of Object.entries(methods)) {
      if (['get', 'post', 'put', 'delete', 'patch'].includes(method)) {
        result[`${method}-${path}`] = true
      }
    }
  }
  return result
})

// 按 tag 分组
const groupedApis = computed(() => {
  if (!apiInfo.value?.paths) return {}
  const schemas = apiInfo.value.components?.schemas || {}
  const groups = {}

  for (const [path, methods] of Object.entries(apiInfo.value.paths)) {
    for (const [method, spec] of Object.entries(methods)) {
      if (!['get', 'post', 'put', 'delete', 'patch'].includes(method)) continue
      const tag = spec.tags?.[0] || '其他'
      if (!groups[tag]) groups[tag] = []

      // 解析请求体 schema
      const bodyRef = spec.requestBody?.content?.['application/json']?.schema?.$ref
      const requestSchema = bodyRef ? resolveRef(bodyRef, schemas) : null

      groups[tag].push({
        method,
        path,
        summary: spec.summary || '',
        description: spec.description?.replace(/\n/g, ' ') || '',
        parameters: (spec.parameters || []).map(p => ({
          name: p.name,
          in: p.in,
          required: !!p.required,
          type: p.schema?.type || p.schema?.$ref?.split('/').pop() || 'any',
          description: p.description || ''
        })),
        requestSchema,
        responses: spec.responses || {}
      })
    }
  }
  return groups
})

function resolveRef(ref, schemas) {
  const name = ref.replace('#/components/schemas/', '')
  return schemas[name] || null
}

function getFieldType(field) {
  if (field.$ref) return field.$ref.split('/').pop()
  if (field.anyOf) return field.anyOf.map(f => f.type || f.$ref?.split('/').pop()).join(' | ')
  return field.type || 'any'
}

function getResponseSchema(resp) {
  const ref = resp?.content?.['application/json']?.schema?.$ref
  return ref ? ref.split('/').pop() : null
}

function methodColor(method) {
  return { get: 'success', post: 'primary', put: 'warning', delete: 'danger', patch: 'info' }[method] || 'info'
}

function codeColor(code) {
  if (code.startsWith('2')) return 'success'
  if (code.startsWith('4')) return 'warning'
  if (code.startsWith('5')) return 'danger'
  return 'info'
}

function toggleGroup(tag) {
  if (openGroups.has(tag)) openGroups.delete(tag)
  else openGroups.add(tag)
}

function toggleApi(api) {
  const key = `${api.method}-${api.path}`
  if (expandedApis.has(key)) expandedApis.delete(key)
  else expandedApis.add(key)
}

onMounted(() => fetchApiDocs())

async function fetchApiDocs() {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/openapi.json')
    apiInfo.value = res.data
    // 默认展开所有 tag
    Object.keys(groupedApis.value).forEach(tag => openGroups.add(tag))
  } catch (e) {
    console.error('获取 API 文档失败:', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.api-docs-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.api-info-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.groups-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.group-block {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f5f7fa;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.group-header:hover {
  background: #ecf5ff;
}

.group-name {
  font-weight: 600;
  font-size: 14px;
  flex: 1;
}

.arrow {
  transition: transform 0.2s;
  color: #909399;
}

.arrow.open {
  transform: rotate(90deg);
}

.api-list {
  padding: 8px 12px;
}

.api-item {
  border-radius: 6px;
  margin-bottom: 6px;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}

.api-item.expanded {
  border-color: #409EFF;
}

.api-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  border-radius: 6px;
  background: #fafafa;
  transition: background 0.2s;
}

.api-row:hover {
  background: #ecf5ff;
}

.method-tag {
  font-family: monospace;
  min-width: 60px;
  text-align: center;
}

.api-path {
  font-family: monospace;
  font-weight: 500;
  color: #303133;
  font-size: 13px;
}

.api-summary {
  color: #909399;
  font-size: 13px;
  flex: 1;
}

.arrow-small {
  color: #c0c4cc;
  transition: transform 0.2s;
  font-size: 12px;
}

.arrow-small.open {
  transform: rotate(90deg);
}

.api-detail {
  padding: 14px 20px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.desc-text {
  color: #606266;
  font-size: 13px;
  margin-bottom: 12px;
  line-height: 1.6;
}

.section {
  margin-top: 14px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 13px;
  background: #409EFF;
  border-radius: 2px;
}

.schema-box {
  background: #f9f9f9;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px 14px;
}

.schema-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  border-bottom: 1px dashed #f0f0f0;
  font-size: 13px;
}

.schema-row:last-child {
  border-bottom: none;
}

.field-name {
  font-family: monospace;
  color: #e6a23c;
  min-width: 120px;
  font-weight: 500;
}

.field-desc {
  color: #909399;
}

.response-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.resp-desc {
  color: #606266;
}

.resp-schema {
  color: #409EFF;
  font-family: monospace;
  font-size: 12px;
}
</style>
