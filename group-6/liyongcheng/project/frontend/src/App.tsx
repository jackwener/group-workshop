import { useState, useEffect, useCallback } from 'react';
import type { Report, StockPrice, ComparisonData } from './types';
import {
  Header,
  Sidebar,
  ReportDetail,
  StockPanel,
  CompareView,
  UploadModal,
  EmptyState,
  ConfirmModal,
  Toast,
} from './components';
import { getReports, uploadReport, deleteReport, compareReports, getStockPrice } from './services/api';

type ViewMode = 'list' | 'detail' | 'compare';

interface ToastState {
  show: boolean;
  message: string;
  type: 'success' | 'error';
}

function App() {
  // 状态管理
  const [reports, setReports] = useState<Report[]>([]);
  const [currentReport, setCurrentReport] = useState<Report | null>(null);
  const [compareList, setCompareList] = useState<Report[]>([]);
  const [stockPrice, setStockPrice] = useState<StockPrice | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  
  // UI状态
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showUpload, setShowUpload] = useState(false);
  const [showStockPanel, setShowStockPanel] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Report | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', type: 'success' });
  
  // LLM状态
  const [llmStatus] = useState<'configured' | 'demo'>('demo');

  // 加载研报列表
  const loadReports = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getReports({ page: 1, page_size: 100 });
      setReports(result.items);
    } catch (error) {
      showToast('加载研报列表失败', 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  // 显示Toast
  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 3000);
  };

  // 选择研报
  const handleSelectReport = (report: Report) => {
    setCurrentReport(report);
    setViewMode('detail');
    setComparisonData(null);
  };

  // 添加到对比列表
  const handleAddToCompare = (report: Report) => {
    if (compareList.length >= 10) {
      showToast('对比列表已满（最多10个）', 'error');
      return;
    }
    if (compareList.find((r) => r.id === report.id)) {
      showToast('该研报已在对比列表中', 'error');
      return;
    }
    setCompareList([...compareList, report]);
    showToast('已添加到对比列表', 'success');
  };

  // 开始对比
  const handleStartCompare = async () => {
    if (compareList.length < 2) {
      showToast('请至少选择2份研报进行对比', 'error');
      return;
    }

    setLoading(true);
    try {
      const subjectCode = compareList[0].subject_code;
      const reportIds = compareList.map((r) => r.id);
      const result = await compareReports(subjectCode, reportIds);
      setComparisonData(result);
      setViewMode('compare');
      setCurrentReport(null);
    } catch (error) {
      showToast('对比失败，请稍后重试', 'error');
    } finally {
      setLoading(false);
    }
  };

  // 上传研报
  const handleUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    setUploadError(null);

    // 模拟进度
    const interval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + 10, 90));
    }, 200);

    try {
      const report = await uploadReport(file);
      setReports([report, ...reports]);
      setShowUpload(false);
      showToast('研报上传成功', 'success');
      setUploadProgress(100);
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : '上传失败');
      setUploadProgress(0);
    } finally {
      clearInterval(interval);
      setUploading(false);
    }
  };

  // 删除研报
  const handleDelete = async () => {
    if (!deleteTarget) return;

    try {
      await deleteReport(deleteTarget.id);
      setReports(reports.filter((r) => r.id !== deleteTarget.id));
      setCompareList(compareList.filter((r) => r.id !== deleteTarget.id));
      if (currentReport?.id === deleteTarget.id) {
        setCurrentReport(null);
        setViewMode('list');
      }
      showToast('研报已删除', 'success');
    } catch (error) {
      showToast('删除失败', 'error');
    } finally {
      setDeleteTarget(null);
    }
  };

  // 查询股价
  const handleQueryStock = async (code: string) => {
    setShowStockPanel(true);
    setLoading(true);
    try {
      const result = await getStockPrice(code);
      setStockPrice(result);
    } catch (error) {
      showToast('查询股价失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  // 返回列表
  const handleBackToList = () => {
    setCurrentReport(null);
    setComparisonData(null);
    setViewMode('list');
  };

  return (
    <div className="h-screen flex flex-col">
      <Header llmStatus={llmStatus} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          reports={reports}
          currentReport={currentReport}
          compareList={compareList}
          onSelectReport={handleSelectReport}
          onAddToCompare={handleAddToCompare}
          onStartCompare={handleStartCompare}
          onUpload={() => setShowUpload(true)}
          loading={loading}
        />

        <main className="flex-1 overflow-y-auto p-6">
          {viewMode === 'list' && reports.length === 0 && (
            <EmptyState onUpload={() => setShowUpload(true)} />
          )}

          {viewMode === 'list' && reports.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reports.map((report) => (
                <div
                  key={report.id}
                  onClick={() => handleSelectReport(report)}
                  className="bg-white rounded-lg shadow-sm p-4 cursor-pointer hover:shadow-md transition-shadow"
                >
                  <h3 className="font-medium text-gray-900 truncate">{report.title}</h3>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-sm text-gray-500">{report.subject_name}</span>
                    <span className="text-xs text-gray-400">{report.author}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs text-gray-400">
                      {report.created_at.slice(0, 10)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {viewMode === 'detail' && currentReport && (
            <ReportDetail
              report={currentReport}
              onClose={handleBackToList}
              onAddToCompare={() => handleAddToCompare(currentReport)}
              onDelete={() => setDeleteTarget(currentReport)}
              onQueryStock={handleQueryStock}
            />
          )}

          {viewMode === 'compare' && comparisonData && (
            <CompareView data={comparisonData} onClose={handleBackToList} />
          )}
        </main>
      </div>

      {/* 弹窗 */}
      {showUpload && (
        <UploadModal
          onUpload={handleUpload}
          onClose={() => {
            setShowUpload(false);
            setUploadError(null);
          }}
          uploading={uploading}
          progress={uploadProgress}
          error={uploadError}
        />
      )}

      {showStockPanel && (
        <StockPanel
          stockPrice={stockPrice}
          loading={loading}
          onQuery={handleQueryStock}
          onClose={() => setShowStockPanel(false)}
        />
      )}

      {deleteTarget && (
        <ConfirmModal
          message={`确定要删除研报 "${deleteTarget.title}" 吗？`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}

      {toast.show && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ show: false, message: '', type: 'success' })}
        />
      )}
    </div>
  );
}

export default App;
