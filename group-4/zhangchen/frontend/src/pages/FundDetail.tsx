import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { fundApi } from '../services/api'
import type { FundWithPrice } from '../types'

export default function FundDetail() {
  const { id } = useParams<{ id: string }>()
  const [fund, setFund] = useState<FundWithPrice | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      const fundId = parseInt(id, 10)
      if (!isNaN(fundId)) {
        fetchFund(fundId)
      }
    }
  }, [id])

  const fetchFund = async (fundId: number) => {
    try {
      const response = await fundApi.getFund(fundId)
      setFund(response.data)
    } catch (error) {
      console.error('获取基金详情失败:', error)
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

  if (!fund) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">基金不存在</p>
        <Link to="/funds" className="text-primary-600 hover:underline mt-2 inline-block">
          返回基金列表
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link to="/funds" className="flex items-center text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-5 h-5 mr-2" />
        返回基金列表
      </Link>

      <div className="card">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{fund.name}</h1>
            <p className="text-gray-500 mt-1">{fund.code}</p>
          </div>
          <span className="badge badge-info">{fund.type}</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          <div>
            <p className="text-sm text-gray-500">最新净值</p>
            <p className="text-2xl font-bold text-gray-900">{fund.latest_nav ? Number(fund.latest_nav).toFixed(4) : '-'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">日涨跌</p>
            <p className={`text-2xl font-bold ${Number(fund.daily_change_rate || 0) >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
              {Number(fund.daily_change_rate || 0) >= 0 ? '+' : ''}{Number(fund.daily_change_rate || 0).toFixed(2)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">基金公司</p>
            <p className="text-lg font-medium text-gray-900">{fund.company}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">风险等级</p>
            <p className="text-lg font-medium text-gray-900">{fund.risk_level}级</p>
          </div>
        </div>

        {fund.description && (
          <div className="mt-6 pt-6 border-t">
            <h3 className="font-medium text-gray-900 mb-2">基金简介</h3>
            <p className="text-gray-600">{fund.description}</p>
          </div>
        )}
      </div>
    </div>
  )
}
