import React, { useState } from 'react';

function AgentModal({ isOpen, onClose, onCreateAgent }) {
  const [newAgent, setNewAgent] = useState({ 
    id: "", 
    name: "", 
    icon: "fa-laptop-code", 
    description: "", 
    welcome: "", 
    system_prompt: "" 
  });

  if (!isOpen) return null;

  const handleSubmit = () => {
    const { id, name, icon, description, welcome, system_prompt } = newAgent;
    if (!id || !name || !description || !welcome || !system_prompt) {
      alert("Vui lòng điền đầy đủ tất cả các trường cấu hình!");
      return;
    }
    onCreateAgent(newAgent);
    onClose();
  };

  return (
    <div className="studio-modal-overlay active">
      <div className="studio-modal-card">
        <div className="studio-modal-header">
          <div className="modal-header-icon"><i className="fa-solid fa-robot"></i></div>
          <div>
            <h3 className="modal-header-title">Khởi tạo Agent mới vào Graph</h3>
            <p className="modal-header-desc">Thiết lập định danh và cấu hình instructions đầu vào cho Node Agent mới.</p>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <div className="studio-modal-body">
          <div className="modal-row">
            <div className="modal-col form-group">
              <label className="form-label">Tên định danh (ID - Slug)</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ví dụ: it_support" 
                value={newAgent.id} 
                onChange={(e) => setNewAgent(prev => ({ ...prev, id: e.target.value }))} 
              />
            </div>
            <div className="modal-col form-group">
              <label className="form-label">Tên hiển thị của Agent</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ví dụ: IT Support Agent" 
                value={newAgent.name} 
                onChange={(e) => setNewAgent(prev => ({ ...prev, name: e.target.value }))} 
              />
            </div>
          </div>
          
          <div className="modal-row">
            <div className="modal-col form-group">
              <label className="form-label">Biểu tượng FontAwesome</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ví dụ: fa-laptop-code" 
                value={newAgent.icon} 
                onChange={(e) => setNewAgent(prev => ({ ...prev, icon: e.target.value }))} 
              />
            </div>
            <div className="modal-col form-group">
              <label className="form-label">Mô tả ngắn gọn vai trò</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ví dụ: Agent giải đáp thắc mắc cài đặt phần mềm..." 
                value={newAgent.description} 
                onChange={(e) => setNewAgent(prev => ({ ...prev, description: e.target.value }))} 
              />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Lời chào chào mừng khách hàng</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Xin chào! Tôi có thể hỗ trợ gì về kỹ thuật cho bạn?" 
              value={newAgent.welcome} 
              onChange={(e) => setNewAgent(prev => ({ ...prev, welcome: e.target.value }))} 
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">System Instruction Prompt (Định hướng LLM)</label>
            <textarea 
              className="form-textarea" 
              rows="4" 
              placeholder="Nhiệm vụ: Bạn chịu trách nhiệm giải đáp và xử lý các ticket..." 
              value={newAgent.system_prompt} 
              onChange={(e) => setNewAgent(prev => ({ ...prev, system_prompt: e.target.value }))} 
            />
          </div>
        </div>
        
        <div className="studio-modal-footer">
          <button className="modal-btn-secondary" onClick={onClose}>Hủy bỏ</button>
          <button className="modal-btn-primary" onClick={handleSubmit}>
            <i className="fa-solid fa-circle-check"></i>
            <span>Khởi tạo & Kích hoạt Agent</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default AgentModal;
