import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <header className="dashboard-header">
          <h1>仪表板</h1>
          <div className="user-info">
            <span>欢迎，{user?.name || user?.username}</span>
            <button onClick={handleLogout} className="btn-secondary">
              退出登录
            </button>
          </div>
        </header>

        <main className="dashboard-content">
          <div className="welcome-card">
            <h2>欢迎使用基金分析系统</h2>
            <p>您已成功登录系统</p>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <h3>基金总数</h3>
              <p className="stat-value">1,234</p>
            </div>
            <div className="stat-card">
              <h3>今日更新</h3>
              <p className="stat-value">56</p>
            </div>
            <div className="stat-card">
              <h3>分析任务</h3>
              <p className="stat-value">12</p>
            </div>
            <Link to="/tetris" className="stat-card" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>
              <h3>休闲娱乐</h3>
              <p className="stat-value">俄罗斯方块</p>
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
