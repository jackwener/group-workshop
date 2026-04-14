import { useEffect, useState } from 'react'
import { Trophy, Medal, Loader2 } from 'lucide-react'
import { rankingApi, contestApi } from '../services/api'
import type { RankingItem, Contest } from '../types'

export default function Rankings() {
  const [rankings, setRankings] = useState<RankingItem[]>([])
  const [contests, setContests] = useState<Contest[]>([])
  const [selectedContest, setSelectedContest] = useState<number | null>(null)
  const [myRank, setMyRank] = useState<number | undefined>(undefined)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchContests()
  }, [])

  useEffect(() => {
    if (selectedContest) {
      fetchRankings(selectedContest)
    }
  }, [selectedContest])

  const fetchContests = async () => {
    try {
      const response = await contestApi.getContests({ status: 'active' })
      setContests(response.data)
      if (response.data.length > 0) {
        setSelectedContest(response.data[0].id)
      }
    } catch (error) {
      console.error('获取比赛列表失败:', error)
    }
  }

  const fetchRankings = async (contestId: number) => {
    try {
      setLoading(true)
      const response = await rankingApi.getContestRankings(contestId)
      setRankings(response.data.rankings)
      setMyRank(response.data.my_rank)
    } catch (error) {
      console.error('获取排行榜失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Medal className="w-6 h-6 text-yellow-500" />
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />
    if (rank === 3) return <Medal className="w-6 h-6 text-amber-600" />
    return <span className="w-6 h-6 flex items-center justify-center font-bold text-gray-500">{rank}</span>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">排行榜</h1>
        <select
          value={selectedContest || ''}
          onChange={(e) => {
            const id = parseInt(e.target.value, 10)
            if (!isNaN(id)) {
              setSelectedContest(id)
            }
          }}
          className="input md:w-64"
        >
          {contests.map((contest) => (
            <option key={contest.id} value={contest.id}>{contest.name}</option>
          ))}
        </select>
      </div>

      {myRank && (
        <div className="card bg-primary-50 border border-primary-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Trophy className="w-6 h-6 text-primary-600 mr-3" />
              <div>
                <p className="text-sm text-gray-600">我的排名</p>
                <p className="text-2xl font-bold text-primary-600">第 {myRank} 名</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th className="w-16">排名</th>
                  <th>用户</th>
                  <th>总资产</th>
                  <th>收益率</th>
                </tr>
              </thead>
              <tbody>
                {rankings.map((item) => (
                  <tr key={item.user_id} className={item.is_me ? 'bg-primary-50' : ''}>
                    <td>{getRankIcon(item.rank)}</td>
                    <td>
                      <div className="flex items-center">
                        <span className="font-medium">{item.nickname || item.username}</span>
                        {item.is_me && (
                          <span className="badge badge-primary ml-2">我</span>
                        )}
                      </div>
                    </td>
                    <td>¥{item.total_assets.toLocaleString()}</td>
                    <td className={Number(item.total_return) >= 0 ? 'text-success-600' : 'text-danger-600'}>
                      {Number(item.total_return) >= 0 ? '+' : ''}{Number(item.total_return).toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
