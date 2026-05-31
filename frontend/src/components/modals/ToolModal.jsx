import React, { useState } from 'react';

function ToolModal({ isOpen, onClose, agents, onCreateTool }) {
  const [newTool, setNewTool] = useState({ 
    id: "", 
    icon: "fa-globe", 
    description: "", 
    agent: "system_admin", 
    category: "Database Query" 
  });

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!newTool.id.trim()) {
      alert("Vui lòng điền tên định danh Tool!");
      return;
    }
    onCreateTool(newTool);
    onClose();
  };

  return (
    <div className="studio-modal-overlay active">
      <div className="studio-modal-card">
        <div className="studio-modal-header">
          <div className="modal-header-icon" style={{ background: 'var(--color-primary)' }}><i className="fa-solid fa-screwdriver-wrench"></i></div>
          <div>
            <h3 className="modal-header-title">Đăng ký & Liên kết Tool</h3>
            <p className="modal-header-desc">Đăng ký các hàm Python, API gọi ngoài để các Agent trong Graph tự động triệu gọi khi cần.</p>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <div className="studio-modal-body">
          <div className="modal-row">
            <div className="modal-col form-group">
              <label className="form-label">Tên định danh hàm (Tool Name - Slug)</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ví dụ: check_weather_api" 
                value={newTool.id} 
                onChange={(e) => setNewTool(prev => ({ ...prev, id: e.target.value }))} 
              />
            </div>
            <div className="modal-col form-group">
              <label className="form-label">Phân nhóm công vụ (Category)</label>
              <select 
                className="form-select" 
                value={newTool.category} 
                onChange={(e) => setNewTool(prev => ({ ...prev, category: e.target.value }))}
              >
                <option value="Database Query">Database Query</option>
                <option value="Vector Search">Vector Search (RAG)</option>
                <option value="Math/Logic">Math/Logic</option>
                <option value="External Web API">External Web API</option>
              </select>
            </div>
          </div>
          
          <div className="modal-row">
            <div className="modal-col form-group">
              <label className="form-label">Biểu tượng FontAwesome</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ví dụ: fa-cloud-sun" 
                value={newTool.icon} 
                onChange={(e) => setNewTool(prev => ({ ...prev, icon: e.target.value }))} 
              />
            </div>
            <div className="modal-col form-group">
              <label className="form-label">Agent phụ trách gọi Tool</label>
              <select 
                className="form-select" 
                value={newTool.agent} 
                onChange={(e) => setNewTool(prev => ({ ...prev, agent: e.target.value }))}
              >
                {Object.keys(agents).map(k => (
                  <option key={k} value={k}>{agents[k].name}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Mô tả chi tiết tác vụ (Rất quan trọng để LLM quyết định triệu gọi)</label>
            <textarea 
              className="form-textarea" 
              rows="3" 
              placeholder="Ví dụ: Gọi API dự báo thời tiết của các vùng miền Việt Nam, cung cấp tham số location..." 
              value={newTool.description} 
              onChange={(e) => setNewTool(prev => ({ ...prev, description: e.target.value }))} 
            />
          </div>
        </div>
        
        <div className="studio-modal-footer">
          <button className="modal-btn-secondary" onClick={onClose}>Hủy bỏ</button>
          <button className="modal-btn-primary" style={{ background: 'var(--color-primary)' }} onClick={handleSubmit}>
            <i className="fa-solid fa-floppy-disk"></i>
            <span>Đăng ký & Liên kết Tool</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ToolModal;
