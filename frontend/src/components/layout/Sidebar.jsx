import React from 'react';
import { NavLink } from 'react-router-dom';

function Sidebar({
  currentUser,
  skillsCount,
  toolsCount,
  usersCount = 0,
  handleLogout,
  conversations = [],
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
}) {
  return (
    <div className="sidebar">
      <div className="brand-header">
        <div className="brand-icon"><i className="fa-solid fa-brain"></i></div>
        <span className="brand-text">Evo Agents</span>
      </div>

      <div className="profile-card">
        <div className="profile-avatar">{currentUser.avatar}</div>
        <div className="profile-info">
          <span className="profile-name">{currentUser.name}</span>
          <span className={`profile-role-badge role-${currentUser.role}`}>{currentUser.role}</span>
        </div>
      </div>

      <div className="nav-links">
        <span className="nav-section-title">Không gian chính</span>

        <NavLink
          to="/chat"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <i className="fa-solid fa-comments"></i>
          <span>Trò chuyện Bot</span>
        </NavLink>

        {currentUser.role === 'admin' && (
          <>
            <span className="nav-section-title" style={{ marginTop: '16px' }}>Thiết đặt Quản trị</span>

            <NavLink
              to="/admin/skills"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <i className="fa-solid fa-wand-magic-sparkles"></i>
              <span>Quản lý Kỹ năng</span>
              <span className="nav-item-badge">{skillsCount}</span>
            </NavLink>

            <NavLink
              to="/admin/tools"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <i className="fa-solid fa-screwdriver-wrench"></i>
              <span>Quản lý Tools</span>
              <span className="nav-item-badge" style={{ background: 'var(--color-primary)' }}>{toolsCount}</span>
            </NavLink>

            <NavLink
              to="/admin/users"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <i className="fa-solid fa-users"></i>
              <span>Quản lý Users</span>
              <span className="nav-item-badge" style={{ background: 'var(--color-accent)' }}>{usersCount}</span>
            </NavLink>
          </>
        )}
      </div>

      {/* Lịch sử hội thoại */}
      <div className="conv-section">
        <div className="conv-section-head">
          <span className="nav-section-title">Lịch sử trò chuyện</span>
          <button className="conv-new-btn" onClick={onNewChat} title="Cuộc trò chuyện mới">
            <i className="fa-solid fa-pen-to-square"></i>
          </button>
        </div>

        <div className="conv-list">
          {conversations.length === 0 && (
            <div className="conv-empty">Chưa có cuộc trò chuyện nào</div>
          )}
          {conversations.map(conv => (
            <div
              key={conv.id}
              className={`conv-item ${conv.id === activeConversationId ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
              title={conv.title}
            >
              <i className="fa-solid fa-message conv-item-icon"></i>
              <span className="conv-item-title">{conv.title || 'Cuộc trò chuyện'}</span>
              <button
                className="conv-del-btn"
                title="Xóa"
                onClick={(e) => { e.stopPropagation(); onDeleteConversation(conv.id); }}
              >
                <i className="fa-solid fa-trash-can"></i>
              </button>
            </div>
          ))}
        </div>
      </div>

      <button className="logout-btn" onClick={handleLogout}>
        <i className="fa-solid fa-arrow-right-from-bracket"></i>
        <span>Đăng xuất</span>
      </button>
    </div>
  );
}

export default Sidebar;
