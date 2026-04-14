<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航 -->
      <el-header>
        <div class="header-content">
          <h1>研报问答助手</h1>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
          >
            <el-menu-item index="/sessions">
              <el-icon><ChatDotRound /></el-icon>
              <span>会话管理</span>
            </el-menu-item>
            <el-menu-item index="/api-docs">
              <el-icon><Document /></el-icon>
              <span>API 文档</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer>
        <span>研报问答助手 v0.1</span>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useSessionStore } from '@/stores'

const route = useRoute()
const sessionStore = useSessionStore()

const activeMenu = computed(() => {
  return route.path.startsWith('/qa') || route.path.startsWith('/history')
    ? '/sessions'
    : route.path
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.el-container {
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: #fff;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  font-size: 20px;
  margin-right: 40px;
}

.header-content .el-menu {
  background-color: transparent;
  border-bottom: none;
}

.header-content .el-menu-item {
  color: #fff !important;
  border-bottom: none !important;
}

.header-content .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.header-content .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-bottom: 2px solid #fff !important;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}

.el-footer {
  background-color: #f5f7fa;
  text-align: center;
  color: #999;
  font-size: 12px;
  line-height: 60px;
  border-top: 1px solid #e4e7ed;
}
</style>
