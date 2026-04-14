---
name: southernfund-ui
description: 应用南方基金网页样式规范进行前端开发。当用户需要创建或修改符合南方基金品牌规范的UI组件、页面样式、CSS变量、按钮、表单、导航栏、卡片等时使用。适用于需要遵循南方基金设计系统的React/Vue/HTML项目。
---

# 南方基金 UI 样式规范

## 快速开始

使用本 skill 时，遵循南方基金品牌规范：
- **主色调**: 南方红 `#E60012`、稳健蓝 `#003B7F`
- **辅助色**: 金色 `#D4A843`、活力橙 `#FF6B35`、成长绿 `#28A745`
- **中性色**: 深灰 `#333`、中灰 `#666`、浅灰 `#999`、边框灰 `#E5E5E5`、背景灰 `#F5F7FA`

## 核心 CSS 变量

```css
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
  --font-family-zh: "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-family-en: "Roboto", "Helvetica Neue", Arial, sans-serif;
  --font-family-number: "DIN Alternate", "Roboto Mono", monospace;
  
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
  --transition-fast: 0.15s ease;
  --transition-base: 0.3s ease;
  --transition-slow: 0.5s ease;
}
```

## 组件规范

### 按钮

#### 主要按钮
```css
.btn-primary {
  background-color: #E60012;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: #CC0010;
  box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
}

.btn-primary:active {
  background-color: #B3000E;
}

.btn-primary:disabled {
  background-color: #FFB3B3;
  cursor: not-allowed;
}
```

#### 次要按钮
```css
.btn-secondary {
  background-color: #003B7F;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: #002D62;
  box-shadow: 0 4px 12px rgba(0, 59, 127, 0.3);
}
```

#### 描边按钮
```css
.btn-outline {
  background-color: transparent;
  color: #003B7F;
  border: 2px solid #003B7F;
  border-radius: 4px;
  padding: 10px 30px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background-color: #003B7F;
  color: #FFFFFF;
}
```

### 导航栏
```css
.navbar {
  background-color: #003B7F;
  height: 70px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-size: 24px;
  font-weight: 700;
  color: #FFFFFF;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  padding: 10px 20px;
  transition: all 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #FFFFFF;
  background-color: rgba(230, 0, 18, 0.8);
  border-radius: 4px;
}
```

### 卡片
```css
.card {
  background-color: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  border-bottom: 2px solid #E5E5E5;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 20px;
  font-weight: 500;
  color: #333333;
}
```

### 表单
```css
/* 输入框 */
.form-control {
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  color: #333333;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #003B7F;
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 59, 127, 0.1);
}

.form-control::placeholder {
  color: #999999;
}

/* 标签 */
.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 8px;
}

/* 错误状态 */
.form-control.error {
  border-color: #DC3545;
}

.error-message {
  color: #DC3545;
  font-size: 12px;
  margin-top: 4px;
}
```

### 表格
```css
.table {
  width: 100%;
  border-collapse: collapse;
  background-color: #FFFFFF;
}

.table thead {
  background-color: #F5F7FA;
}

.table th {
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #333333;
  text-align: left;
  border-bottom: 2px solid #E5E5E5;
}

.table td {
  padding: 14px 16px;
  font-size: 14px;
  color: #666666;
  border-bottom: 1px solid #E5E5E5;
}

.table tbody tr:hover {
  background-color: #F5F7FA;
}

/* 金融数据表格 */
.table-finance .positive {
  color: #28A745;
  font-weight: 500;
}

.table-finance .negative {
  color: #DC3545;
  font-weight: 500;
}
```

### 标签与徽章
```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 12px;
}

.badge-primary {
  background-color: rgba(230, 0, 18, 0.1);
  color: #E60012;
}

.badge-secondary {
  background-color: rgba(0, 59, 127, 0.1);
  color: #003B7F;
}

.badge-success {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28A745;
}
```

## 响应式设计

```css
/* 容器 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .navbar {
    height: 60px;
  }
  
  .container {
    padding: 0 16px;
  }
  
  .card {
    padding: 16px;
  }
  
  h1 { font-size: 28px; }
  h2 { font-size: 24px; }
  h3 { font-size: 20px; }
}

/* 触摸优化 */
.btn, .nav-link, a {
  min-height: 44px;
  min-width: 44px;
}
```

## 设计原则

1. **主次分明**: 红色用于强调，蓝色用于信任，比例建议 1:3
2. **克制使用**: 页面主色不超过3种，避免视觉混乱
3. **对比度**: 文字与背景对比度不低于 4.5:1 (WCAG AA标准)
4. **金融属性**: 整体色调偏稳重型，避免过于跳跃的色彩
5. **数据可视化**: 红涨绿跌（A股惯例）

## 命名规范

使用 BEM 命名规范:
```css
.block {}
.block__element {}
.block--modifier {}

/* 示例 */
.nav {}
.nav__item {}
.nav__item--active {}
.card {}
.card__header {}
.card--featured {}
```

## 附加资源

- 完整的样式规范详见 [reference.md](reference.md)
