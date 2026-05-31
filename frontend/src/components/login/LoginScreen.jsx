import React from 'react';
import { useNavigate } from 'react-router-dom';

function LoginScreen({ handleQuickLogin }) {
  const navigate = useNavigate();

  const onLogin = (userId) => {
    handleQuickLogin(userId);
    navigate('/chat');
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
        
        <div className="login-form">
          <div className="login-select-wrapper">
            <span className="login-select-icon"><i className="fa-solid fa-user-shield"></i></span>
            <select id="loginUserSelect" className="login-select" defaultValue="adm_001" onChange={(e) => onLogin(e.target.value)}>
              <option value="" disabled>-- Chọn tài khoản --</option>
              <option value="adm_001">Nguyen Admin (ADMIN)</option>
              <option value="acc_001">Le Van C (ACCOUNTANT)</option>
              <option value="emp_001">Nguyen Van A (EMPLOYEE)</option>
            </select>
          </div>
          
          <button className="login-btn" onClick={() => onLogin("adm_001")}>
            <span>Đăng nhập hệ thống (Mặc định Admin)</span>
            <i className="fa-solid fa-arrow-right-to-bracket"></i>
          </button>
        </div>
        
        <div className="login-demo-accounts">
          <p className="demo-accounts-title">Lựa chọn tài khoản Demo nhanh</p>
          <div className="demo-grid">
            <div className="demo-badge" onClick={() => onLogin('adm_001')}>🔑 Quản trị viên (Admin)</div>
            <div className="demo-badge" onClick={() => onLogin('emp_001')}>👥 Nhân viên (Employee)</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginScreen;
