/**
 * 路由配置
 * 基于 05-用户故事与验收标准.md
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/sessions'
  },
  {
    path: '/sessions',
    name: 'Sessions',
    component: () => import('@/views/Sessions.vue'),
    meta: { title: '会话管理' }
  },
  {
    path: '/qa/:sessionId',
    name: 'QA',
    component: () => import('@/views/QA.vue'),
    meta: { title: '问答' }
  },
  {
    path: '/history/:sessionId',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { title: '历史记录' }
  },
  {
    path: '/api-docs',
    name: 'ApiDocs',
    component: () => import('@/views/ApiDocs.vue'),
    meta: { title: 'API 文档' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '研报问答助手'
  next()
})

export default router
