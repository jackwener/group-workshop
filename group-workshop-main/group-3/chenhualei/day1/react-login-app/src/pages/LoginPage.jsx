import LoginForm from '../components/LoginForm';

const LoginPage = () => {
  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>欢迎使用</h1>
          <p>请登录您的账户</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage;
