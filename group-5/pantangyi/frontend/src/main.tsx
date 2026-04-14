import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './index.css'

// 南方基金蓝色主题配置
const customTheme = {
  token: {
    // 主色调 - 南方基金蓝
    colorPrimary: '#0052cc',
    colorPrimaryHover: '#003d8f',
    colorPrimaryActive: '#002766',
    
    // 辅助色
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    
    // 背景色
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f5f7fa',
    
    // 边框色
    colorBorder: '#e8ecf1',
    
    // 文字色
    colorText: '#1a1a1a',
    colorTextSecondary: '#666666',
    colorTextTertiary: '#999999',
    
    // 圆角
    borderRadius: 8,
    
    // 字体
    fontFamily: "'PingFang SC', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  components: {
    Button: {
      primaryColor: '#ffffff',
      borderRadius: 6,
    },
    Input: {
      borderRadius: 8,
      hoverBorderColor: '#0052cc',
      activeBorderColor: '#0052cc',
    },
    Tag: {
      borderRadius: 12,
    },
    Card: {
      borderRadius: 12,
    },
    Modal: {
      borderRadius: 12,
    },
  },
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN} theme={customTheme}>
      <App />
    </ConfigProvider>
  </React.StrictMode>,
)
