import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, TrendingUp, TrendingDown, Loader2 } from 'lucide-react'
import { fundApi } from '../services/api'
import type { FundWithPrice } from '../types'

export default function Funds() {
  const [funds, setFunds] = useState<FundWithPrice[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('')
  const [fundTypes, setFundTypes] = useState<string[]>([])

  useEffect(() => {
    fetchFunds()
    fetchFundTypes()
  }, [])

  const fetchFunds = async () => {
    try {
      const response = await fundApi.getFunds({ limit: 50 })
      setFunds(response.data)
    } catch (error) {
      console.error('获取基金列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchFundTypes = async () => {
    try {
      const response = await fundApi.getFundTypes()
      setFundTypes(response.data)
    } catch (error) {
      console.error('获取基金类型失败:', error)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchFunds()
      return
    }
    try {
      setLoading(true)
      const response = await fundApi.searchFunds(searchQuery)
      setFunds(response.data)
    } catch (error) {
      console.error('搜索基金失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredFunds = selectedType
    ? funds.filter(fund => fund.type === selectedType)
    : funds

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">基金列表</h1>

      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="input pl-10"
            placeholder="搜索基金名称或代码..."
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        </div>
        <button onClick={handleSearch} className="btn-primary">
          搜索
        </button>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="input md:w-48"
        >
          <option value="">全部类型</option>
          {fundTypes.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* 基金列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredFunds.map((fund) => (
          <Link
            key={fund.id}
            to={`/funds/${fund.id}`}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-gray-900">{fund.name}</h3>
                <p className="text-sm text-gray-500">{fund.code}</p>
              </div>
              {fund.daily_change_rate !== undefined && (
                <span className={`flex items-center text-sm font-medium ${
                  Number(fund.daily_change_rate) >= 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {Number(fund.daily_change_rate) >= 0 ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  )}
                  {Number(fund.daily_change_rate) >= 0 ? '+' : ''}{Number(fund.daily_change_rate).toFixed(2)}%
                </span>
              )}
            </div>
            
            <div className="flex justify-between items-end mt-4">
              <div>
                <p className="text-xs text-gray-500">最新净值</p>
                <p className="text-xl font-bold text-gray-900">
                  {fund.latest_nav ? Number(fund.latest_nav).toFixed(4) : '-'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">类型</p>
                <span className="badge badge-info">{fund.type}</span>
              </div>
            </div>
            
            {fund.risk_level && (
              <div className="mt-3 pt-3 border-t">
                <div className="flex items-center text-sm text-gray-500">
                  <span>风险等级:</span>
                  <div className="flex ml-2">
                    {[1, 2, 3, 4, 5].map((level) => (
                      <div
                        key={level}
                        className={`w-2 h-2 rounded-full mr-1 ${
                          level <= fund.risk_level! ? 'bg-danger-500' : 'bg-gray-200'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </Link>
        ))}
      </div>

      {filteredFunds.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">没有找到符合条件的基金</p>
        </div>
      )}
    </div>
  )
}
