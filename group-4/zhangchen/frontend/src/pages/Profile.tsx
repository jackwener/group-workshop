import { useEffect, useState } from 'react'
import { Loader2, User, Mail, Calendar } from 'lucide-react'
import { userApi } from '../services/api'
import type { UserProfile } from '../types'

export default function Profile() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await userApi.getStatistics()
      setProfile(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">无法加载用户信息</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">个人资料</h1>

      <div className="card">
        <div className="flex items-center mb-6">
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
            <User className="w-10 h-10 text-primary-600" />
          </div>
          <div className="ml-6">
            <h2 className="text-xl font-bold text-gray-900">{profile.nickname || profile.username}</h2>
            <p className="text-gray-500">@{profile.username}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center">
            <Mail className="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <p className="text-sm text-gray-500">邮箱</p>
              <p className="font-medium">{profile.email}</p>
            </div>
          </div>
          <div className="flex items-center">
            <Calendar className="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <p className="text-sm text-gray-500">注册时间</p>
              <p className="font-medium">{new Date(profile.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-sm text-gray-500">参加的比赛</p>
          <p className="text-2xl font-bold text-gray-900">{profile.total_contests}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">活跃比赛</p>
          <p className="text-2xl font-bold text-gray-900">{profile.active_contests}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">总收益率</p>
          <p className={`text-2xl font-bold ${Number(profile.total_return) >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
            {Number(profile.total_return) >= 0 ? '+' : ''}{Number(profile.total_return).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}
