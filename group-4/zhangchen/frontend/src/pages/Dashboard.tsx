import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  Trophy, 
  Wallet, 
  ArrowRight,
  Loader2 
} from 'lucide-react'
import { contestApi, userApi } from '../services/api'
import type { Contest, UserProfile } from '../types'

export default function Dashboard() {
  const [contests, setContests] = useState<Contest[]>([])
  const [statistics, setStatistics] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [contestsRes, statsRes] = await Promise.all([
        contestApi.getContests({ limit: 5 }),
        userApi.getStatistics()
      ])
      setContests(contestsRes.data)
      setStatistics(statsRes.data)
    } catch (error) {
      console.error('获取数据失败:', error)
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

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">首页</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">参加的比赛</p>
              <p className="text-2xl font-bold text-gray-900">{statistics?.total_contests || 0}</p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <Trophy className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">活跃比赛</p>
              <p className="text-2xl font-bold text-gray-900">{statistics?.active_contests || 0}</p>
            </div>
            <div className="p-3 bg-success-100 rounded-lg">
              <Wallet className="w-6 h-6 text-success-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">总收益率</p>
              <p className={`text-2xl font-bold ${Number(statistics?.total_return || 0) >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                {Number(statistics?.total_return || 0).toFixed(2)}%
              </p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>
      </div>

      {/* 最近比赛 */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">最近比赛</h2>
          <Link to="/contests" className="text-primary-600 hover:text-primary-700 flex items-center text-sm">
            查看全部 <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

        {contests.length === 0 ? (
          <p className="text-gray-500 text-center py-8">暂无比赛</p>
        ) : (
          <div className="space-y-3">
            {contests.map((contest) => (
              <Link
                key={contest.id}
                to={`/contests/${contest.id}`}
                className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900">{contest.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      初始资金: ¥{contest.initial_balance.toLocaleString()}
                    </p>
                  </div>
                  <span className={`badge ${
                    contest.status === 'active' ? 'badge-success' :
                    contest.status === 'pending' ? 'badge-warning' :
                    'badge-secondary'
                  }`}>
                    {contest.status === 'active' ? '进行中' :
                     contest.status === 'pending' ? '未开始' :
                     '已结束'}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
