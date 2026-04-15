import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchMe } from './store/authSlice'
import type { RootState, AppDispatch } from './store'

// 布局
import MainLayout from './components/layout/MainLayout'

// 页面
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Funds from './pages/Funds'
import FundDetail from './pages/FundDetail'
import Contests from './pages/Contests'
import ContestDetail from './pages/ContestDetail'
import Portfolio from './pages/Portfolio'
import Rankings from './pages/Rankings'
import Transactions from './pages/Transactions'
import Profile from './pages/Profile'

// 路由守卫组件
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth)
  return !isAuthenticated ? <>{children}</> : <Navigate to="/" />
}

function App() {
  const dispatch = useDispatch<AppDispatch>()
  const { isAuthenticated } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchMe())
    }
  }, [dispatch, isAuthenticated])

  return (
    <Routes>
      {/* 公开路由 */}
      <Route path="/login" element={
        <PublicRoute>
          <Login />
        </PublicRoute>
      } />
      <Route path="/register" element={
        <PublicRoute>
          <Register />
        </PublicRoute>
      } />

      {/* 受保护路由 */}
      <Route path="/" element={
        <PrivateRoute>
          <MainLayout />
        </PrivateRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="funds" element={<Funds />} />
        <Route path="funds/:id" element={<FundDetail />} />
        <Route path="contests" element={<Contests />} />
        <Route path="contests/:id" element={<ContestDetail />} />
        <Route path="portfolio" element={<Portfolio />} />
        <Route path="rankings" element={<Rankings />} />
        <Route path="transactions" element={<Transactions />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
