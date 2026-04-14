/**
 * Markdown to HTML Generator
 * 将 repowiki/zh/content 目录下的所有 Markdown 文件转换为 HTML
 * 使用南方基金样式规范
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 简单的 Markdown 解析器
function parseMarkdown(content) {
  let html = content;
  
  // 处理 mermaid 图表 (需要在代码块之前处理)
  html = html.replace(/```mermaid\n([\s\S]*?)```/g, (match, diagram) => {
    return `<div class="mermaid">${diagram.trim()}</div>`;
  });
  
  // 处理代码块 (```...```)
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    const langClass = lang ? ` class="language-${lang}"` : '';
    return `<pre><code${langClass}>${escapeHtml(code.trim())}</code></pre>`;
  });
  
  // 处理行内代码 (`...`)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // 处理标题
  html = html.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
  html = html.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
  html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  // 处理引用块
  html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');
  
  // 处理无序列表 - 改进版本
  const lines = html.split('\n');
  let result = [];
  let inList = false;
  let listItems = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const listMatch = line.match(/^(\s*)[-*+] (.*)$/);
    
    if (listMatch) {
      if (!inList) {
        inList = true;
        listItems = [];
      }
      listItems.push(`<li>${listMatch[2]}</li>`);
    } else {
      if (inList) {
        result.push('<ul>' + listItems.join('') + '</ul>');
        inList = false;
        listItems = [];
      }
      result.push(line);
    }
  }
  
  if (inList) {
    result.push('<ul>' + listItems.join('') + '</ul>');
  }
  
  html = result.join('\n');
  
  // 处理表格
  html = html.replace(/\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)/g, (match, header, rows) => {
    const headers = header.split('|').map(h => h.trim()).filter(h => h);
    const rowData = rows.trim().split('\n').map(row => {
      return row.split('|').map(c => c.trim()).filter(c => c);
    });
    
    let tableHtml = '<table><thead><tr>';
    headers.forEach(h => {
      tableHtml += `<th>${h}</th>`;
    });
    tableHtml += '</tr></thead><tbody>';
    
    rowData.forEach(row => {
      tableHtml += '<tr>';
      row.forEach(cell => {
        tableHtml += `<td>${cell}</td>`;
      });
      tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';
    
    return tableHtml;
  });
  
  // 处理链接 [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  
  // 处理粗体
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  
  // 处理斜体
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
  
  // 处理水平线
  html = html.replace(/^---+$/gim, '<hr>');
  
  // 处理段落
  const paragraphs = html.split('\n\n');
  html = paragraphs.map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<')) return p;
    return `<p>${p}</p>`;
  }).join('\n');
  
  // 处理 cite 标签
  html = html.replace(/<cite>([\s\S]*?)<\/cite>/g, '<div class="cite-block">$1</div>');
  
  return html;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// 生成 HTML 模板
function generateHTML(title, content, relativePath) {
  const parsedContent = parseMarkdown(content);
  
  // 生成面包屑导航
  const breadcrumb = generateBreadcrumb(relativePath);
  
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} - React Login App 文档</title>
  <link rel="stylesheet" href="${getRelativePath(relativePath)}assets/styles.css">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>📚 项目文档</h1>
      </div>
      <nav class="sidebar-nav">
        ${generateSidebar(relativePath)}
      </nav>
    </aside>
    
    <main class="main-content">
      <div class="breadcrumb">
        ${breadcrumb}
      </div>
      
      <article class="content">
        ${parsedContent}
      </article>
      
      <footer class="page-footer">
        <p>React Login App 项目文档</p>
      </footer>
    </main>
  </div>
  
  <script>
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true
      }
    });
  </script>
</body>
</html>`;
}

// 生成面包屑导航
function generateBreadcrumb(relativePath) {
  const parts = relativePath.split('/').filter(p => p && p !== 'content');
  let breadcrumb = '<a href="index.html">首页</a>';
  let currentPath = '';
  
  parts.forEach((part, index) => {
    currentPath += '../';
    const name = part.replace('.md', '').replace('.html', '');
    if (index === parts.length - 1) {
      breadcrumb += ` / <span>${name}</span>`;
    } else {
      breadcrumb += ` / <a href="${currentPath}index.html">${name}</a>`;
    }
  });
  
  return breadcrumb;
}

// 获取相对路径
function getRelativePath(relativePath) {
  const depth = relativePath.split('/').filter(p => p && p !== 'content').length - 1;
  return '../'.repeat(Math.max(0, depth));
}

// 生成侧边栏导航
function generateSidebar(currentPath) {
  const structure = {
    '项目概述': '项目概述.html',
    '快速开始': '快速开始.html',
    '架构设计': {
      'index': '架构设计/架构设计.html',
      '组件架构': '架构设计/组件架构.html',
      '状态管理': '架构设计/状态管理.html',
      '路由系统': '架构设计/路由系统.html',
      '构建配置': '架构设计/构建配置.html'
    },
    '认证系统': {
      'index': '认证系统/认证系统.html',
      '认证状态管理': '认证系统/认证状态管理.html',
      '登录表单验证': '认证系统/登录表单验证.html',
      '路由保护机制': '认证系统/路由保护机制.html',
      '认证流程详解': '认证系统/认证流程详解.html'
    },
    '仪表板功能': '仪表板功能.html',
    '俄罗斯方块游戏': {
      'index': '俄罗斯方块游戏/俄罗斯方块游戏.html',
      '游戏引擎核心': '俄罗斯方块游戏/游戏引擎核心.html',
      '方块系统': '俄罗斯方块游戏/方块系统.html',
      '物理机制': '俄罗斯方块游戏/物理机制.html',
      '输入处理': '俄罗斯方块游戏/输入处理.html',
      '界面渲染': '俄罗斯方块游戏/界面渲染.html',
      '游戏状态管理': '俄罗斯方块游戏/游戏状态管理.html'
    },
    '开发工具配置': {
      'index': '开发工具配置/开发工具配置.html',
      'Vite 构建配置': '开发工具配置/Vite 构建配置.html',
      'ESLint 代码规范': '开发工具配置/ESLint 代码规范.html',
      '包依赖管理': '开发工具配置/包依赖管理.html',
      '版本控制忽略规则': '开发工具配置/版本控制忽略规则.html'
    },
    '样式系统': '样式系统.html',
    '部署指南': '部署指南.html'
  };
  
  let html = '<ul>';
  
  for (const [name, item] of Object.entries(structure)) {
    if (typeof item === 'string') {
      const href = getRelativePath(currentPath) + item;
      html += `<li><a href="${href}">${name}</a></li>`;
    } else {
      html += `<li class="has-submenu">`;
      html += `<span class="submenu-title">${name}</span>`;
      html += '<ul class="submenu">';
      
      for (const [subName, subHref] of Object.entries(item)) {
        if (subName === 'index') continue;
        const fullHref = getRelativePath(currentPath) + subHref;
        html += `<li><a href="${fullHref}">${subName}</a></li>`;
      }
      
      html += '</ul></li>';
    }
  }
  
  html += '</ul>';
  return html;
}

// 递归获取所有 Markdown 文件
function getMarkdownFiles(dir, baseDir = dir) {
  const files = [];
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      files.push(...getMarkdownFiles(fullPath, baseDir));
    } else if (item.endsWith('.md')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

// 主函数
function main() {
  const contentDir = path.join(__dirname, 'content');
  const outputDir = path.join(__dirname, 'html');
  const assetsDir = path.join(outputDir, 'assets');
  
  // 创建输出目录
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
  }
  
  // 复制并创建 CSS 文件
  const cssContent = generateCSS();
  fs.writeFileSync(path.join(assetsDir, 'styles.css'), cssContent);
  
  // 获取所有 Markdown 文件
  const mdFiles = getMarkdownFiles(contentDir);
  
  console.log(`找到 ${mdFiles.length} 个 Markdown 文件`);
  
  // 处理每个文件
  for (const file of mdFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const relativePath = path.relative(contentDir, file);
    const title = path.basename(file, '.md');
    
    // 生成 HTML
    const html = generateHTML(title, content, relativePath);
    
    // 确定输出路径
    const outputPath = path.join(outputDir, relativePath.replace('.md', '.html'));
    const outputFileDir = path.dirname(outputPath);
    
    // 确保目录存在
    if (!fs.existsSync(outputFileDir)) {
      fs.mkdirSync(outputFileDir, { recursive: true });
    }
    
    // 写入文件
    fs.writeFileSync(outputPath, html);
    console.log(`✓ 生成: ${relativePath.replace('.md', '.html')}`);
  }
  
  // 生成首页
  generateIndexPage(outputDir);
  
  console.log('\n✅ HTML 生成完成！');
  console.log(`📁 输出目录: ${outputDir}`);
}

// 生成首页
function generateIndexPage(outputDir) {
  const indexHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>React Login App 文档</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>📚 项目文档</h1>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li><a href="项目概述.html">项目概述</a></li>
          <li><a href="快速开始.html">快速开始</a></li>
          <li class="has-submenu">
            <span class="submenu-title">架构设计</span>
            <ul class="submenu">
              <li><a href="架构设计/架构设计.html">架构设计</a></li>
              <li><a href="架构设计/组件架构.html">组件架构</a></li>
              <li><a href="架构设计/状态管理.html">状态管理</a></li>
              <li><a href="架构设计/路由系统.html">路由系统</a></li>
              <li><a href="架构设计/构建配置.html">构建配置</a></li>
            </ul>
          </li>
          <li class="has-submenu">
            <span class="submenu-title">认证系统</span>
            <ul class="submenu">
              <li><a href="认证系统/认证系统.html">认证系统</a></li>
              <li><a href="认证系统/认证状态管理.html">认证状态管理</a></li>
              <li><a href="认证系统/登录表单验证.html">登录表单验证</a></li>
              <li><a href="认证系统/路由保护机制.html">路由保护机制</a></li>
              <li><a href="认证系统/认证流程详解.html">认证流程详解</a></li>
            </ul>
          </li>
          <li><a href="仪表板功能.html">仪表板功能</a></li>
          <li class="has-submenu">
            <span class="submenu-title">俄罗斯方块游戏</span>
            <ul class="submenu">
              <li><a href="俄罗斯方块游戏/俄罗斯方块游戏.html">俄罗斯方块游戏</a></li>
              <li><a href="俄罗斯方块游戏/游戏引擎核心.html">游戏引擎核心</a></li>
              <li><a href="俄罗斯方块游戏/方块系统.html">方块系统</a></li>
              <li><a href="俄罗斯方块游戏/物理机制.html">物理机制</a></li>
              <li><a href="俄罗斯方块游戏/输入处理.html">输入处理</a></li>
              <li><a href="俄罗斯方块游戏/界面渲染.html">界面渲染</a></li>
              <li><a href="俄罗斯方块游戏/游戏状态管理.html">游戏状态管理</a></li>
            </ul>
          </li>
          <li class="has-submenu">
            <span class="submenu-title">开发工具配置</span>
            <ul class="submenu">
              <li><a href="开发工具配置/开发工具配置.html">开发工具配置</a></li>
              <li><a href="开发工具配置/Vite 构建配置.html">Vite 构建配置</a></li>
              <li><a href="开发工具配置/ESLint 代码规范.html">ESLint 代码规范</a></li>
              <li><a href="开发工具配置/包依赖管理.html">包依赖管理</a></li>
              <li><a href="开发工具配置/版本控制忽略规则.html">版本控制忽略规则</a></li>
            </ul>
          </li>
          <li><a href="样式系统.html">样式系统</a></li>
          <li><a href="部署指南.html">部署指南</a></li>
        </ul>
      </nav>
    </aside>
    
    <main class="main-content">
      <div class="hero-section">
        <h1>React Login App 项目文档</h1>
        <p>基于 React 19 + Vite 的登录应用，包含用户认证、仪表板和俄罗斯方块游戏功能</p>
        <div class="hero-actions">
          <a href="项目概述.html" class="btn btn-primary">开始阅读</a>
          <a href="快速开始.html" class="btn btn-secondary">快速开始</a>
        </div>
      </div>
      
      <div class="feature-grid">
        <div class="feature-card">
          <h3>🔐 认证系统</h3>
          <p>基于 Zustand 的状态管理，React Hook Form + Zod 表单验证，路由保护机制</p>
          <a href="认证系统/认证系统.html">了解更多 →</a>
        </div>
        <div class="feature-card">
          <h3>🎮 俄罗斯方块</h3>
          <p>完整的游戏引擎，包含方块系统、物理机制、输入处理和界面渲染</p>
          <a href="俄罗斯方块游戏/俄罗斯方块游戏.html">了解更多 →</a>
        </div>
        <div class="feature-card">
          <h3>⚡ 现代技术栈</h3>
          <p>React 19、Vite 8、React Router 7，快速开发体验</p>
          <a href="开发工具配置/开发工具配置.html">了解更多 →</a>
        </div>
      </div>
    </main>
  </div>
</body>
</html>`;
  
  fs.writeFileSync(path.join(outputDir, 'index.html'), indexHtml);
  console.log('✓ 生成: index.html');
}

// 生成 CSS 样式（基于南方基金规范）
function generateCSS() {
  return `/* 南方基金风格文档样式 */

:root {
  /* 品牌色 */
  --color-primary: #E60012;
  --color-primary-dark: #CC0010;
  --color-secondary: #003B7F;
  --color-secondary-dark: #002D62;
  
  /* 辅助色 */
  --color-gold: #D4A843;
  --color-orange: #FF6B35;
  --color-green: #28A745;
  
  /* 中性色 */
  --color-text-dark: #333333;
  --color-text-base: #666666;
  --color-text-light: #999999;
  --color-border: #E5E5E5;
  --color-background: #F5F7FA;
  --color-white: #FFFFFF;
  
  /* 状态色 */
  --color-success: #28A745;
  --color-warning: #FFC107;
  --color-error: #DC3545;
  --color-info: #17A2B8;
  
  /* 字体 */
  --font-family-zh: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  --font-family-en: "Roboto", "Helvetica Neue", Arial, sans-serif;
  --font-family-mono: "SF Mono", "Roboto Mono", Consolas, monospace;
  
  /* 字号 */
  --font-size-h1: 36px;
  --font-size-h2: 28px;
  --font-size-h3: 24px;
  --font-size-h4: 20px;
  --font-size-base: 16px;
  --font-size-sm: 14px;
  --font-size-xs: 12px;
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-xxl: 48px;
  
  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  /* 阴影 */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 6px 20px rgba(0, 0, 0, 0.12);
  
  /* 动画 */
  --transition-base: 0.3s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-zh);
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--color-text-base);
  background-color: var(--color-background);
}

/* 布局 */
.layout {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background-color: var(--color-white);
  border-right: 1px solid var(--color-border);
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-secondary);
}

.sidebar-header h1 {
  font-size: var(--font-size-h4);
  color: var(--color-white);
  font-weight: 600;
}

.sidebar-nav {
  padding: var(--spacing-md) 0;
}

.sidebar-nav ul {
  list-style: none;
}

.sidebar-nav li {
  position: relative;
}

.sidebar-nav a,
.sidebar-nav .submenu-title {
  display: block;
  padding: var(--spacing-sm) var(--spacing-lg);
  color: var(--color-text-dark);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);
  cursor: pointer;
}

.sidebar-nav a:hover {
  background-color: rgba(0, 59, 127, 0.08);
  color: var(--color-secondary);
}

.sidebar-nav .has-submenu > .submenu-title {
  font-weight: 500;
  color: var(--color-text-dark);
}

.sidebar-nav .submenu {
  padding-left: var(--spacing-lg);
}

.sidebar-nav .submenu a {
  color: var(--color-text-base);
  font-size: var(--font-size-xs);
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 280px;
  padding: var(--spacing-xl) var(--spacing-xxl);
  max-width: calc(100% - 280px);
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.breadcrumb a {
  color: var(--color-secondary);
  text-decoration: none;
}

.breadcrumb a:hover {
  color: var(--color-primary);
}

.breadcrumb span {
  color: var(--color-text-dark);
  font-weight: 500;
}

/* 内容区域 */
.content {
  background-color: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
}

/* 标题 */
h1, h2, h3, h4, h5, h6 {
  color: var(--color-text-dark);
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: var(--spacing-md);
}

h1 {
  font-size: var(--font-size-h1);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--color-primary);
  margin-bottom: var(--spacing-xl);
}

h2 {
  font-size: var(--font-size-h2);
  margin-top: var(--spacing-xxl);
  color: var(--color-secondary);
}

h3 {
  font-size: var(--font-size-h3);
  margin-top: var(--spacing-xl);
}

h4 {
  font-size: var(--font-size-h4);
  margin-top: var(--spacing-lg);
}

h5 {
  font-size: var(--font-size-base);
  margin-top: var(--spacing-lg);
}

h6 {
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-md);
}

/* 段落 */
p {
  margin-bottom: var(--spacing-md);
}

/* 链接 */
a {
  color: var(--color-secondary);
  text-decoration: none;
  transition: color var(--transition-base);
}

a:hover {
  color: var(--color-primary);
}

/* 列表 */
ul, ol {
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-xl);
}

li {
  margin-bottom: var(--spacing-xs);
}

/* 引用块 */
blockquote {
  border-left: 4px solid var(--color-primary);
  padding-left: var(--spacing-md);
  margin: var(--spacing-md) 0;
  color: var(--color-text-base);
  font-style: italic;
}

/* 代码 */
code {
  font-family: var(--font-family-mono);
  font-size: 0.9em;
  background-color: var(--color-background);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  color: var(--color-error);
}

pre {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin-bottom: var(--spacing-md);
}

pre code {
  background-color: transparent;
  color: inherit;
  padding: 0;
}

/* 表格 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--spacing-md);
  background-color: var(--color-white);
}

th, td {
  padding: var(--spacing-sm) var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  background-color: var(--color-background);
  font-weight: 600;
  color: var(--color-text-dark);
}

tr:hover {
  background-color: var(--color-background);
}

/* 水平线 */
hr {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: var(--spacing-xl) 0;
}

/* 引用块样式 */
.cite-block {
  background-color: var(--color-background);
  border-left: 4px solid var(--color-secondary);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.cite-block p {
  margin-bottom: var(--spacing-sm);
}

.cite-block p:last-child {
  margin-bottom: 0;
}

/* Mermaid 图表 */
.mermaid {
  text-align: center;
  margin: var(--spacing-lg) 0;
  padding: var(--spacing-md);
  background-color: var(--color-white);
  border-radius: var(--radius-md);
}

/* 页脚 */
.page-footer {
  margin-top: var(--spacing-xxl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  text-align: center;
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
}

/* 首页样式 */
.hero-section {
  text-align: center;
  padding: var(--spacing-xxl) 0;
  margin-bottom: var(--spacing-xxl);
}

.hero-section h1 {
  border-bottom: none;
  margin-bottom: var(--spacing-md);
}

.hero-section p {
  font-size: var(--font-size-h4);
  color: var(--color-text-base);
  margin-bottom: var(--spacing-xl);
}

.hero-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
}

/* 按钮 */
.btn {
  display: inline-block;
  padding: 12px 32px;
  font-size: var(--font-size-base);
  font-weight: 500;
  border-radius: var(--radius-sm);
  text-decoration: none;
  transition: all var(--transition-base);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
  color: var(--color-white);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: var(--color-white);
}

.btn-secondary:hover {
  background-color: var(--color-secondary-dark);
  box-shadow: 0 4px 12px rgba(0, 59, 127, 0.3);
  color: var(--color-white);
}

/* 特性卡片 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.feature-card {
  background-color: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.feature-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.feature-card h3 {
  margin-top: 0;
  color: var(--color-secondary);
}

.feature-card p {
  margin-bottom: var(--spacing-md);
}

.feature-card a {
  color: var(--color-primary);
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: relative;
    height: auto;
  }
  
  .main-content {
    margin-left: 0;
    max-width: 100%;
    padding: var(--spacing-md);
  }
  
  .layout {
    flex-direction: column;
  }
  
  h1 {
    font-size: 28px;
  }
  
  h2 {
    font-size: 24px;
  }
  
  h3 {
    font-size: 20px;
  }
  
  .hero-actions {
    flex-direction: column;
  }
}

/* 打印样式 */
@media print {
  .sidebar {
    display: none;
  }
  
  .main-content {
    margin-left: 0;
    max-width: 100%;
  }
}
`;
}

// 运行主函数
main();
