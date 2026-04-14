import { useEffect, useState } from 'react'
import { Loader2, ArrowUpCircle, ArrowDownCircle } from 'lucide-react'
import { transactionApi } from '../services/api'
import type { TransactionWithFund } from '../types'

export default function Transactions() {
  const [transactions, setTransactions] = useState<TransactionWithFund[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTransactions()
  }, [])

  const fetchTransactions = async () => {
    try {
      const response = await transactionApi.getTransactions()
      setTransactions(response.data)
    } catch (error) {
      console.error('获取交易记录失败:', error)
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
      <h1 className="text-2xl font-bold text-gray-900">交易记录</h1>

      <div className="card">
        {transactions.length === 0 ? (
          <p className="text-gray-500 text-center py-8">暂无交易记录</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>类型</th>
                  <th>基金</th>
                  <th>份额</th>
                  <th>净值</th>
                  <th>金额</th>
                  <th>手续费</th>
                  <th>时间</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>
                      <div className="flex items-center">
                        {transaction.transaction_type === 'buy' ? (
                          <ArrowUpCircle className="w-5 h-5 text-success-600 mr-2" />
                        ) : (
                          <ArrowDownCircle className="w-5 h-5 text-danger-600 mr-2" />
                        )}
                        <span className={transaction.transaction_type === 'buy' ? 'text-success-600' : 'text-danger-600'}>
                          {transaction.transaction_type === 'buy' ? '买入' : '卖出'}
                        </span>
                      </div>
                    </td>
                    <td>
                      <div>
                        <p className="font-medium">{transaction.fund_name}</p>
                        <p className="text-sm text-gray-500">{transaction.fund_code}</p>
                      </div>
                    </td>
                    <td>{Number(transaction.shares).toFixed(4)}</td>
                    <td>¥{Number(transaction.nav).toFixed(4)}</td>
                    <td>¥{Number(transaction.amount).toLocaleString()}</td>
                    <td>¥{Number(transaction.fee).toFixed(2)}</td>
                    <td>{new Date(transaction.transaction_date).toLocaleString()}</td>
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
