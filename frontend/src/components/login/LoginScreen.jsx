import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginScreen({ handleLogin }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.');
      return;
    }
    setError('');
    setLoading(true);
    const err = await handleLogin(username.trim(), password.trim());
    setLoading(false);
    if (err) {
      setError(err);
    } else {
      navigate('/chat');
    }
  };

  return (
    <div className="login-screen">
      <div className="bg-glow-container">
        <div className="bg-blob blob1"></div>
        <div className="bg-blob blob2"></div>
      </div>
      <div className="login-card">
        <div className="login-logo"><i className="fa-solid fa-brain"></i></div>
        <h1 className="login-title">Evo Agents Portal</h1>
        <p className="login-subtitle">Hệ thống Multi-Agent & Kích hoạt Kỹ năng động</p>

        <form className="login-form" onSubmit={onSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="login-username">Tên đăng nhập</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon"><i className="fa-solid fa-user"></i></span>
              <input
                id="login-username"
                type="text"
                className="login-input"
                placeholder="Nhập username..."
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                autoFocus
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">Mật khẩu</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon"><i className="fa-solid fa-lock"></i></span>
              <input
                id="login-password"
                type="password"
                className="login-input"
                placeholder="Nhập mật khẩu..."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
          </div>

          {error && <div className="login-error">{error}</div>}

          <button className="login-btn" type="submit" disabled={loading}>
            {loading
              ? <><i className="fa-solid fa-spinner fa-spin"></i><span>Đang xác thực...</span></>
              : <><span>Đăng nhập</span><i className="fa-solid fa-arrow-right-to-bracket"></i></>
            }
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginScreen;
