import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, Trophy, Users, Calendar } from 'lucide-react'
import { contestApi } from '../services/api'
import type { ContestDetail as ContestDetailType } from '../types'

export default function ContestDetail() {
  const { id } = useParams<{ id: string }>()
  const [contest, setContest] = useState<ContestDetailType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      const contestId = parseInt(id, 10)
      if (!isNaN(contestId)) {
        fetchContest(contestId)
      }
    }
  }, [id])

  const fetchContest = async (contestId: number) => {
    try {
      const response = await contestApi.getContest(contestId)
      setContest(response.data)
    } catch (error) {
      console.error('获取比赛详情失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleJoin = async () => {
    if (!id) return
    const contestId = parseInt(id, 10)
    if (isNaN(contestId)) return
    try {
      await contestApi.joinContest(contestId)
      fetchContest(contestId)
    } catch (error) {
      console.error('参加比赛失败:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (!contest) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">比赛不存在</p>
        <Link to="/contests" className="text-primary-600 hover:underline mt-2 inline-block">
          返回比赛列表
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link to="/contests" className="flex items-center text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-5 h-5 mr-2" />
        返回比赛列表
      </Link>

      <div className="card">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{contest.name}</h1>
            <span className={`badge mt-2 ${
              contest.status === 'active' ? 'badge-success' :
              contest.status === 'pending' ? 'badge-warning' :
              'badge-secondary'
            }`}>
              {contest.status === 'active' ? '进行中' :
               contest.status === 'pending' ? '未开始' :
               '已结束'}
            </span>
          </div>
          {!contest.is_participating && contest.status !== 'ended' && (
            <button onClick={handleJoin} className="btn-primary">
              参加比赛
            </button>
          )}
          {contest.is_participating && (
            <span className="badge badge-success">已参加</span>
          )}
        </div>

        {contest.description && (
          <p className="text-gray-600 mt-4">{contest.description}</p>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 pt-6 border-t">
          <div>
            <p className="text-sm text-gray-500">初始资金</p>
            <p className="text-xl font-bold text-gray-900">¥{contest.initial_balance.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">参赛人数</p>
            <p className="text-xl font-bold text-gray-900">{contest.participant_count}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">开始时间</p>
            <p className="text-lg font-medium text-gray-900">{new Date(contest.start_date).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">结束时间</p>
            <p className="text-lg font-medium text-gray-900">{new Date(contest.end_date).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
