import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Trophy, Users, Calendar, Loader2 } from 'lucide-react'
import { contestApi } from '../services/api'
import type { Contest } from '../types'

export default function Contests() {
  const [contests, setContests] = useState<Contest[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchContests()
  }, [])

  const fetchContests = async () => {
    try {
      const response = await contestApi.getContests({ limit: 50 })
      setContests(response.data)
    } catch (error) {
      console.error('获取比赛列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredContests = contests.filter(contest => {
    if (filter === 'all') return true
    return contest.status === filter
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="badge badge-success">进行中</span>
      case 'pending':
        return <span className="badge badge-warning">未开始</span>
      case 'ended':
        return <span className="badge badge-secondary">已结束</span>
      default:
        return null
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
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">比赛列表</h1>
        <Link to="/contests/create" className="btn-primary flex items-center">
          <Plus className="w-5 h-5 mr-2" />
          创建比赛
        </Link>
      </div>

      {/* 筛选 */}
      <div className="flex gap-2">
        {[
          { key: 'all', label: '全部' },
          { key: 'active', label: '进行中' },
          { key: 'pending', label: '未开始' },
          { key: 'ended', label: '已结束' },
        ].map((item) => (
          <button
            key={item.key}
            onClick={() => setFilter(item.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === item.key
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* 比赛列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredContests.map((contest) => (
          <Link
            key={contest.id}
            to={`/contests/${contest.id}`}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center">
                <Trophy className="w-5 h-5 text-primary-600 mr-2" />
                <h3 className="font-semibold text-gray-900">{contest.name}</h3>
              </div>
              {getStatusBadge(contest.status)}
            </div>

            {contest.description && (
              <p className="text-sm text-gray-500 mb-3 line-clamp-2">{contest.description}</p>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center text-gray-600">
                <Wallet className="w-4 h-4 mr-2" />
                <span>初始资金: ¥{contest.initial_balance.toLocaleString()}</span>
              </div>
              <div className="flex items-center text-gray-600">
                <Calendar className="w-4 h-4 mr-2" />
                <span>
                  {new Date(contest.start_date).toLocaleDateString()} - 
                  {new Date(contest.end_date).toLocaleDateString()}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filteredContests.length === 0 && (
        <div className="text-center py-12">
          <Trophy className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">暂无比赛</p>
        </div>
      )}
    </div>
  )
}
