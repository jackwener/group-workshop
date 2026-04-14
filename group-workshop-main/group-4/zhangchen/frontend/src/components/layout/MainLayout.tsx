import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { 
  LayoutDashboard, 
  TrendingUp, 
  Trophy, 
  Wallet, 
  History,
  User,
  LogOut,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'
import { logout } from '../../store/authSlice'
import type { RootState, AppDispatch } from '../../store'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: '首页' },
  { path: '/funds', icon: TrendingUp, label: '基金' },
  { path: '/contests', icon: Trophy, label: '比赛' },
  { path: '/portfolio', icon: Wallet, label: '投资组合' },
  { path: '/rankings', icon: Trophy, label: '排行榜' },
  { path: '/transactions', icon: History, label: '交易记录' },
]

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const { user } = useSelector((state: RootState) => state.auth)

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* 侧边栏 - 桌面端 */}
      <aside className="hidden md:flex flex-col w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-primary-600">基金模拟投资</h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-primary-50 text-primary-600' 
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        
        <div className="p-4 border-t">
          <Link
            to="/profile"
            className="flex items-center px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-50"
          >
            <User className="w-5 h-5 mr-3" />
            {user?.nickname || user?.username}
          </Link>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-50 mt-1"
          >
            <LogOut className="w-5 h-5 mr-3" />
            退出登录
          </button>
        </div>
      </aside>

      {/* 移动端侧边栏 */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div 
            className="absolute inset-0 bg-black/50"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="absolute left-0 top-0 h-full w-64 bg-white shadow-lg">
            <div className="p-6 border-b flex justify-between items-center">
              <h1 className="text-xl font-bold text-primary-600">基金模拟投资</h1>
              <button onClick={() => setSidebarOpen(false)}>
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <nav className="p-4 space-y-1">
              {menuItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-primary-50 text-primary-600' 
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </aside>
        </div>
      )}

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* 移动端头部 */}
        <header className="md:hidden bg-white shadow-sm p-4 flex justify-between items-center">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-bold text-primary-600">基金模拟投资</h1>
          <div className="w-6" />
        </header>

        {/* 页面内容 */}
        <div className="flex-1 p-6 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
