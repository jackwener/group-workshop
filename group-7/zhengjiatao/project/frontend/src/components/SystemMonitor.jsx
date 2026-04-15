import { useState, useEffect } from 'react';
import styles from './SystemMonitor.module.css';
import { getSystemStatus } from '../services/api';

function SystemMonitor() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState(false);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await getSystemStatus();
      setStatus(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 定时刷新
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // 30秒刷新一次
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (percent) => {
    if (percent < 50) return styles.good;
    if (percent < 80) return styles.warning;
    return styles.critical;
  };

  if (!expanded) {
    return (
      <button 
        className={styles.monitorBtn}
        onClick={() => setExpanded(true)}
        title="查看系统状态"
      >
        <span className={styles.monitorIcon}>📊</span>
        系统状态
      </button>
    );
  }

  return (
    <div className={styles.monitorPanel}>
      <div className={styles.panelHeader}>
        <h3>系统监控</h3>
        <div className={styles.panelActions}>
          <button 
            className={styles.refreshBtn}
            onClick={fetchStatus}
            disabled={loading}
          >
            {loading ? '刷新中...' : '刷新'}
          </button>
          <button 
            className={styles.closeBtn}
            onClick={() => setExpanded(false)}
          >
            ✕
          </button>
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {status && (
        <div className={styles.statusContent}>
          <div className={styles.statusRow}>
            <span className={styles.statusLabel}>系统状态:</span>
            <span className={`${styles.statusValue} ${
              status.status === 'healthy' ? styles.healthy : 
              status.status === 'warning' ? styles.warning : styles.error
            }`}>
              {status.status === 'healthy' ? '健康' : 
               status.status === 'warning' ? '警告' : '错误'}
            </span>
          </div>

          <div className={styles.metrics}>
            <div className={styles.metric}>
              <div className={styles.metricLabel}>CPU</div>
              <div className={styles.metricBar}>
                <div 
                  className={`${styles.metricFill} ${getStatusColor(status.cpu_percent)}`}
                  style={{ width: `${Math.min(status.cpu_percent, 100)}%` }}
                />
              </div>
              <div className={styles.metricValue}>{status.cpu_percent}%</div>
            </div>

            <div className={styles.metric}>
              <div className={styles.metricLabel}>内存</div>
              <div className={styles.metricBar}>
                <div 
                  className={`${styles.metricFill} ${getStatusColor(status.memory_percent)}`}
                  style={{ width: `${Math.min(status.memory_percent, 100)}%` }}
                />
              </div>
              <div className={styles.metricValue}>
                {status.memory_percent}% ({status.memory_used_mb}MB / {status.memory_total_mb}MB)
              </div>
            </div>

            <div className={styles.metric}>
              <div className={styles.metricLabel}>磁盘</div>
              <div className={styles.metricBar}>
                <div 
                  className={`${styles.metricFill} ${getStatusColor(status.disk_percent)}`}
                  style={{ width: `${Math.min(status.disk_percent, 100)}%` }}
                />
              </div>
              <div className={styles.metricValue}>{status.disk_percent}%</div>
            </div>
          </div>

          <div className={styles.timestamp}>
            更新时间: {new Date(status.timestamp).toLocaleString('zh-CN')}
          </div>
        </div>
      )}
    </div>
  );
}

export default SystemMonitor;
