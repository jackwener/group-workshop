import { useState, useCallback } from 'react';
import type { Report } from '../types';

interface HeaderProps {
  llmStatus: 'configured' | 'demo' | 'checking';
}

export function Header({ llmStatus }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-semibold text-gray-900">研报阅读系统</h1>
      <div className="flex items-center gap-2">
        {llmStatus === 'configured' && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            LLM 已配置
          </span>
        )}
        {llmStatus === 'demo' && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            离线演示
          </span>
        )}
      </div>
    </header>
  );
}

interface SidebarProps {
  reports: Report[];
  currentReport: Report | null;
  compareList: Report[];
  onSelectReport: (report: Report) => void;
  onAddToCompare: (report: Report) => void;
  onStartCompare: () => void;
  onUpload: () => void;
  loading: boolean;
}

export function Sidebar({
  reports,
  currentReport,
  compareList,
  onSelectReport,
  onAddToCompare,
  onStartCompare,
  onUpload,
  loading,
}: SidebarProps) {
  return (
    <aside className="w-72 bg-white border-r border-gray-200 flex flex-col">
      {/* 上传按钮 */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onUpload}
          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + 上传研报
        </button>
      </div>

      {/* 研报列表 */}
      <div className="flex-1 overflow-y-auto p-4">
        <h2 className="text-sm font-medium text-gray-500 mb-3">研报列表</h2>
        {loading ? (
          <div className="text-center py-4 text-gray-400">加载中...</div>
        ) : reports.length === 0 ? (
          <div className="text-center py-4 text-gray-400">暂无研报</div>
        ) : (
          <ul className="space-y-2">
            {reports.map((report) => (
              <li key={report.id}>
                <div
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    currentReport?.id === report.id
                      ? 'bg-primary-50 border border-primary-200'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                  onClick={() => onSelectReport(report)}
                >
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {report.title}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-500">{report.author}</span>
                    <RatingBadge rating={report.rating} />
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* 对比列表 */}
      {compareList.length > 0 && (
        <div className="p-4 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            对比列表 ({compareList.length}/10)
          </h3>
          <ul className="space-y-1 mb-3">
            {compareList.map((report) => (
              <li key={report.id} className="text-xs text-gray-600 flex items-center gap-1">
                <span className="w-2 h-2 bg-primary-400 rounded-full"></span>
                {report.title.slice(0, 15)}...
              </li>
            ))}
          </ul>
          <button
            onClick={onStartCompare}
            disabled={compareList.length < 2}
            className="w-full px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            开始对比
          </button>
        </div>
      )}
    </aside>
  );
}

export function RatingBadge({ rating }: { rating: string }) {
  const colors: Record<string, string> = {
    '买入': 'bg-green-100 text-green-800',
    '增持': 'bg-blue-100 text-blue-800',
    '中性': 'bg-gray-100 text-gray-800',
    '减持': 'bg-orange-100 text-orange-800',
    '卖出': 'bg-red-100 text-red-800',
  };

  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${colors[rating] || 'bg-gray-100 text-gray-800'}`}>
      {rating}
    </span>
  );
}

export function TrendTag({ trend }: { trend: string }) {
  const labels: Record<string, string> = {
    'bullish': '看涨',
    'bearish': '看跌',
    'neutral': '中性',
  };
  
  const colors: Record<string, string> = {
    'bullish': 'bg-red-100 text-red-800',
    'bearish': 'bg-green-100 text-green-800',
    'neutral': 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors[trend] || colors['neutral']}`}>
      {labels[trend] || '中性'}
    </span>
  );
}

export function ParseStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    'success': 'bg-green-100 text-green-800',
    'partial': 'bg-orange-100 text-orange-800',
    'failed': 'bg-red-100 text-red-800',
  };

  const labels: Record<string, string> = {
    'success': '解析成功',
    'partial': '部分解析',
    'failed': '解析失败',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors[status] || colors['failed']}`}>
      {labels[status] || '未知'}
    </span>
  );
}

interface ReportDetailProps {
  report: Report;
  onClose: () => void;
  onAddToCompare: () => void;
  onDelete: () => void;
  onQueryStock: (code: string) => void;
}

export function ReportDetail({ report, onClose, onAddToCompare, onDelete, onQueryStock }: ReportDetailProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-start justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex-1">{report.title}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 ml-4">
          ✕
        </button>
      </div>

      <div className="space-y-4">
        {/* 研究对象 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">研究对象:</span>
          <button
            onClick={() => onQueryStock(report.subject_code)}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            {report.subject_name} ({report.subject_code})
          </button>
          <ParseStatusBadge status={report.parse_status} />
        </div>

        {/* 券商 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">券商:</span>
          <span className="text-gray-900">{report.author}</span>
        </div>

        {/* 评级和方向 */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">评级:</span>
            <RatingBadge rating={report.rating} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">方向:</span>
            <TrendTag trend={report.trend} />
          </div>
        </div>

        {/* 目标价 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">目标价:</span>
          <span className="text-lg font-semibold text-gray-900">
            {report.target_price ? `¥${report.target_price.toLocaleString()}` : '未设定'}
          </span>
        </div>

        {/* 核心观点 */}
        <div>
          <span className="text-sm text-gray-500 block mb-2">核心观点:</span>
          <p className="text-gray-700 text-sm leading-relaxed">{report.summary}</p>
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-2 pt-4 border-t border-gray-100">
          <button
            onClick={onAddToCompare}
            className="px-4 py-2 text-sm bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100"
          >
            添加对比
          </button>
          <button
            onClick={onDelete}
            className="px-4 py-2 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  );
}

interface StockPanelProps {
  stockPrice: {
    code: string;
    name: string;
    price: number;
    change: number;
    change_percent: number;
    open: number;
    high: number;
    low: number;
    volume: number;
    amount: number;
    source: string;
  } | null;
  loading: boolean;
  onQuery: (code: string) => void;
  onClose: () => void;
}

export function StockPanel({ stockPrice, loading, onQuery, onClose }: StockPanelProps) {
  const [code, setCode] = useState('');

  const handleQuery = useCallback(() => {
    if (code.trim()) {
      onQuery(code.trim());
    }
  }, [code, onQuery]);

  return (
    <div className="fixed right-4 top-20 w-80 bg-white rounded-lg shadow-lg p-4 z-50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900">股价查询</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
      </div>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="输入股票代码"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
        />
        <button
          onClick={handleQuery}
          disabled={loading || !code.trim()}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? '查询中...' : '查询'}
        </button>
      </div>

      {stockPrice && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-medium">{stockPrice.name}</span>
            <span className="text-xs text-gray-400">{stockPrice.source}</span>
          </div>
          
          <div className="flex items-end gap-2">
            <span className="text-2xl font-bold">¥{stockPrice.price.toFixed(2)}</span>
            <span className={`text-sm ${stockPrice.change >= 0 ? 'text-red-500' : 'text-green-500'}`}>
              {stockPrice.change >= 0 ? '+' : ''}{stockPrice.change.toFixed(2)} ({stockPrice.change_percent.toFixed(2)}%)
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
            <div>开盘: ¥{stockPrice.open.toFixed(2)}</div>
            <div>最高: ¥{stockPrice.high.toFixed(2)}</div>
            <div>最低: ¥{stockPrice.low.toFixed(2)}</div>
            <div>成交量: {(stockPrice.volume / 10000).toFixed(0)}万手</div>
          </div>
        </div>
      )}
    </div>
  );
}

interface CompareViewProps {
  data: {
    subject_name: string;
    subject_code: string;
    report_count: number;
    comparison: Array<{
      report_id: string;
      author: string;
      rating: string;
      trend: string;
      target_price: number | null;
      summary: string;
      publish_date: string;
    }>;
  };
  onClose: () => void;
}

export function CompareView({ data, onClose }: CompareViewProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">研报对比</h2>
          <p className="text-sm text-gray-500 mt-1">
            {data.subject_name} ({data.subject_code}) - 共 {data.report_count} 份研报
          </p>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-medium text-gray-500">对比维度</th>
              {data.comparison.map((item) => (
                <th key={item.report_id} className="text-center py-3 px-4 font-medium text-gray-900">
                  {item.author}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-gray-100">
              <td className="py-3 px-4 text-gray-500">评级</td>
              {data.comparison.map((item) => (
                <td key={item.report_id} className="text-center py-3 px-4">
                  <RatingBadge rating={item.rating} />
                </td>
              ))}
            </tr>
            <tr className="border-b border-gray-100">
              <td className="py-3 px-4 text-gray-500">方向</td>
              {data.comparison.map((item) => (
                <td key={item.report_id} className="text-center py-3 px-4">
                  <TrendTag trend={item.trend} />
                </td>
              ))}
            </tr>
            <tr className="border-b border-gray-100">
              <td className="py-3 px-4 text-gray-500">目标价</td>
              {data.comparison.map((item) => (
                <td key={item.report_id} className="text-center py-3 px-4 font-medium">
                  {item.target_price ? `¥${item.target_price.toLocaleString()}` : '-'}
                </td>
              ))}
            </tr>
            <tr className="border-b border-gray-100">
              <td className="py-3 px-4 text-gray-500">核心观点</td>
              {data.comparison.map((item) => (
                <td key={item.report_id} className="text-left py-3 px-4 text-gray-600 text-xs max-w-xs">
                  {item.summary}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 text-gray-500">日期</td>
              {data.comparison.map((item) => (
                <td key={item.report_id} className="text-center py-3 px-4 text-gray-500 text-xs">
                  {item.publish_date}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface UploadModalProps {
  onUpload: (file: File) => void;
  onClose: () => void;
  uploading: boolean;
  progress: number;
  error: string | null;
}

export function UploadModal({ onUpload, onClose, uploading, progress, error }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);

  const handleUpload = () => {
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-medium mb-4">上传研报</h3>

        <div className="mb-4">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
          />
          <p className="mt-2 text-xs text-gray-400">仅支持 PDF 格式，最大 20MB</p>
        </div>

        {uploading && (
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1 text-center">上传中... {progress}%</p>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            disabled={uploading}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {uploading ? '上传中...' : '上传'}
          </button>
        </div>
      </div>
    </div>
  );
}

export function EmptyState({ onUpload }: { onUpload: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <div className="text-6xl mb-4">📄</div>
      <h2 className="text-xl font-medium text-gray-900 mb-2">暂无研报</h2>
      <p className="text-gray-500 mb-6">上传研报开始分析</p>
      <button
        onClick={onUpload}
        className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
      >
        上传研报
      </button>
    </div>
  );
}

export function ConfirmModal({
  message,
  onConfirm,
  onCancel,
}: {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-sm">
        <p className="text-gray-700 mb-6">{message}</p>
        <div className="flex justify-end gap-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            确认
          </button>
        </div>
      </div>
    </div>
  );
}

export function Toast({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) {
  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';

  return (
    <div className={`fixed top-4 right-4 ${bgColor} text-white px-4 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2`}>
      <span>{message}</span>
      <button onClick={onClose} className="text-white hover:text-gray-200">✕</button>
    </div>
  );
}
