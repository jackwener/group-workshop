import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Loader2, Wallet, TrendingUp, TrendingDown } from 'lucide-react'
import { portfolioApi, contestApi } from '../services/api'
import type { PortfolioOverview, Contest } from '../types'

export default function Portfolio() {
  const [searchParams] = useSearchParams()
  const [portfolio, setPortfolio] = useState<PortfolioOverview | null>(null)
  const [contests, setContests] = useState<Contest[]>([])
  const [selectedContest, setSelectedContest] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchContests()
  }, [])

  useEffect(() => {
    const contestId = searchParams.get('contest')
    if (contestId) {
      const id = parseInt(contestId, 10)
      if (!isNaN(id)) {
        setSelectedContest(id)
        fetchPortfolio(id)
      }
    }
  }, [searchParams])

  const fetchContests = async () => {
    try {
      const response = await contestApi.getContests({ status: 'active' })
      setContests(response.data)
      if (response.data.length > 0 && !selectedContest) {
        setSelectedContest(response.data[0].id)
        fetchPortfolio(response.data[0].id)
      }
    } catch (error) {
      console.error('获取比赛列表失败:', error)
    }
  }

  const fetchPortfolio = async (contestId: number) => {
    try {
      setLoading(true)
      const response = await portfolioApi.getOverview(contestId)
      setPortfolio(response.data)
    } catch (error) {
      console.error('获取投资组合失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleContestChange = (contestId: number) => {
    setSelectedContest(contestId)
    fetchPortfolio(contestId)
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
        <h1 className="text-2xl font-bold text-gray-900">投资组合</h1>
        <select
          value={selectedContest || ''}
          onChange={(e) => {
            const id = parseInt(e.target.value, 10)
            if (!isNaN(id)) {
              handleContestChange(id)
            }
          }}
          className="input md:w-64"
        >
          <option value="">选择比赛</option>
          {contests.map((contest) => (
            <option key={contest.id} value={contest.id}>{contest.name}</option>
          ))}
        </select>
      </div>

      {portfolio ? (
        <>
          {/* 资产概览 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card">
              <p className="text-sm text-gray-500">总资产</p>
              <p className="text-2xl font-bold text-gray-900">¥{portfolio.total_assets.toLocaleString()}</p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-500">现金余额</p>
              <p className="text-2xl font-bold text-gray-900">¥{portfolio.cash_balance.toLocaleString()}</p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-500">持仓市值</p>
              <p className="text-2xl font-bold text-gray-900">¥{portfolio.market_value.toLocaleString()}</p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-500">总收益率</p>
              <p className={`text-2xl font-bold ${Number(portfolio.total_return_rate) >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                {Number(portfolio.total_return_rate) >= 0 ? '+' : ''}{Number(portfolio.total_return_rate).toFixed(2)}%
              </p>
            </div>
          </div>

          {/* 持仓列表 */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">持仓明细</h2>
            {portfolio.holdings.length === 0 ? (
              <p className="text-gray-500 text-center py-8">暂无持仓</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>基金名称</th>
                      <th>持有份额</th>
                      <th>平均成本</th>
                      <th>当前净值</th>
                      <th>市值</th>
                      <th>盈亏</th>
                      <th>收益率</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.holdings.map((holding) => (
                      <tr key={holding.fund_id}>
                        <td>
                          <div>
                            <p className="font-medium">{holding.fund_name}</p>
                            <p className="text-sm text-gray-500">{holding.fund_code}</p>
                          </div>
                        </td>
                        <td>{Number(holding.shares).toFixed(4)}</td>
                        <td>¥{Number(holding.avg_cost).toFixed(4)}</td>
                        <td>¥{Number(holding.current_nav).toFixed(4)}</td>
                        <td>¥{holding.market_value.toLocaleString()}</td>
                        <td className={holding.profit_loss >= 0 ? 'text-success-600' : 'text-danger-600'}>
                          {holding.profit_loss >= 0 ? '+' : ''}¥{holding.profit_loss.toLocaleString()}
                        </td>
                        <td className={Number(holding.return_rate) >= 0 ? 'text-success-600' : 'text-danger-600'}>
                          {Number(holding.return_rate) >= 0 ? '+' : ''}{Number(holding.return_rate).toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="card text-center py-12">
          <Wallet className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">请先选择一个比赛查看投资组合</p>
        </div>
      )}
    </div>
  )
}
