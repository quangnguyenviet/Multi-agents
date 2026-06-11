import React, { useState } from 'react';
import { apiFetch, apiRequestJson, readJsonResponse } from '../../api';

const ROLES = ['admin', 'user'];

function UserManager({ currentUser, users, onRefresh }) {
  const [form, setForm] = useState({ username: '', password: '', name: '', role: 'user' });
  const [editTarget, setEditTarget] = useState(null); // { id, name, role, password }
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  /* ── TẠO USER MỚI ── */
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password || !form.name) {
      setError('Điền đầy đủ username, mật khẩu và tên hiển thị.');
      return;
    }
    setSaving(true); setError('');
    try {
      const { response: res, data } = await apiRequestJson(`/api/users?admin_id=${currentUser.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) { setError(data.detail || 'Tạo user thất bại'); return; }
      setForm({ username: '', password: '', name: '', role: 'user' });
      onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  /* ── LƯU SỬA ── */
  const handleUpdate = async () => {
    if (!editTarget) return;
    setSaving(true); setError('');
    const body = {};
    if (editTarget.name)     body.name = editTarget.name;
    if (editTarget.role)     body.role = editTarget.role;
    if (editTarget.password) body.password = editTarget.password;
    try {
      const res = await apiFetch(`/api/users/${editTarget.id}?admin_id=${currentUser.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) { const d = await readJsonResponse(res); setError(d.detail || 'Cập nhật thất bại'); return; }
      setEditTarget(null);
      onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  /* ── XÓA USER ── */
  const handleDelete = async (uid, username) => {
    if (!window.confirm(`Xóa user "${username}"?`)) return;
    try {
      const res = await apiFetch(`/api/users/${uid}?admin_id=${currentUser.id}`, { method: 'DELETE' });
      if (!res.ok) { const d = await readJsonResponse(res); alert(d.detail || 'Xóa thất bại'); return; }
      onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="tab-content active">
      <div className="panel-header">
        <div className="panel-header-left">
          <div className="panel-icon"><i className="fa-solid fa-users"></i></div>
          <div>
            <h2 className="panel-title">Quản lý Users</h2>
            <p className="panel-desc">Thêm, sửa, xóa tài khoản đăng nhập hệ thống</p>
          </div>
        </div>
        <span className="nav-item-badge" style={{ fontSize: '13px', padding: '4px 10px' }}>
          {users.length} users
        </span>
      </div>

      {/* ── FORM THÊM USER ── */}
      <div className="user-add-section">
        <h3 className="user-section-title">Thêm user mới</h3>
        {error && <div className="user-error">{error}</div>}
        <form className="user-add-form" onSubmit={handleCreate}>
          <input
            className="user-input"
            placeholder="Username"
            value={form.username}
            onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
          />
          <input
            className="user-input"
            type="password"
            placeholder="Mật khẩu"
            value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
          />
          <input
            className="user-input"
            placeholder="Tên hiển thị"
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          />
          <select
            className="user-input"
            value={form.role}
            onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
          >
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <button className="user-add-btn" type="submit" disabled={saving}>
            {saving ? <i className="fa-solid fa-spinner fa-spin"></i> : <i className="fa-solid fa-plus"></i>}
            Tạo user
          </button>
        </form>
      </div>

      {/* ── BẢNG DANH SÁCH ── */}
      <div className="user-table-wrapper">
        <table className="user-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Tên hiển thị</th>
              <th>Role</th>
              <th>Tạo lúc</th>
              <th style={{ width: 120 }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>Chưa có user nào</td></tr>
            )}
            {users.map(u => (
              <tr key={u.id} className={u.id === currentUser.id ? 'user-row-me' : ''}>
                <td><code className="user-username">{u.username}</code></td>
                <td>{u.name}</td>
                <td><span className={`role-badge role-${u.role}`}>{u.role}</span></td>
                <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {u.created_at ? new Date(u.created_at).toLocaleDateString('vi-VN') : '—'}
                </td>
                <td>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button
                      className="user-action-btn edit"
                      title="Sửa"
                      onClick={() => setEditTarget({ id: u.id, name: u.name, role: u.role, password: '' })}
                    >
                      <i className="fa-solid fa-pen"></i>
                    </button>
                    {u.id !== currentUser.id && (
                      <button
                        className="user-action-btn delete"
                        title="Xóa"
                        onClick={() => handleDelete(u.id, u.username)}
                      >
                        <i className="fa-solid fa-trash"></i>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── MODAL SỬA ── */}
      {editTarget && (
        <div className="user-modal-overlay" onClick={() => setEditTarget(null)}>
          <div className="user-modal" onClick={e => e.stopPropagation()}>
            <h3 className="user-modal-title">Sửa user</h3>
            {error && <div className="user-error">{error}</div>}
            <div className="form-group">
              <label className="form-label">Tên hiển thị</label>
              <input
                className="user-input"
                value={editTarget.name}
                onChange={e => setEditTarget(t => ({ ...t, name: e.target.value }))}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Role</label>
              <select
                className="user-input"
                value={editTarget.role}
                onChange={e => setEditTarget(t => ({ ...t, role: e.target.value }))}
              >
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Mật khẩu mới (để trống = không đổi)</label>
              <input
                className="user-input"
                type="password"
                placeholder="Để trống nếu không đổi..."
                value={editTarget.password}
                onChange={e => setEditTarget(t => ({ ...t, password: e.target.value }))}
              />
            </div>
            <div className="user-modal-actions">
              <button className="user-cancel-btn" onClick={() => setEditTarget(null)}>Hủy</button>
              <button className="user-save-btn" onClick={handleUpdate} disabled={saving}>
                {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserManager;
