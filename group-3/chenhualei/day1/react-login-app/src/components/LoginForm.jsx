import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import useAuthStore from '../store/authStore';
import { useNavigate } from 'react-router-dom';

const loginSchema = z.object({
  username: z.string().min(1, '请输入用户名'),
  password: z.string().min(6, '密码至少6位'),
});

const LoginForm = () => {
  const navigate = useNavigate();
  const { login, loading, error } = useAuthStore();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    const result = await login(data.username, data.password);
    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="login-form">
      <h2>用户登录</h2>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-group">
          <label htmlFor="username">用户名</label>
          <input
            id="username"
            type="text"
            {...register('username')}
            placeholder="请输入用户名"
            disabled={loading}
          />
          {errors.username && (
            <span className="error">{errors.username.message}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password">密码</label>
          <input
            id="password"
            type="password"
            {...register('password')}
            placeholder="请输入密码"
            disabled={loading}
          />
          {errors.password && (
            <span className="error">{errors.password.message}</span>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? '登录中...' : '登录'}
        </button>

        <div className="hint">
          <p>测试账号：admin / 123456</p>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;
