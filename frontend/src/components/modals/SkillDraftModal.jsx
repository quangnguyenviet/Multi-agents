import React from 'react';

function SkillDraftModal({ skillDraft, setSkillDraft, onPublishSkill }) {
  if (!skillDraft) return null;

  const handlePublish = () => {
    onPublishSkill();
  };

  return (
    <div className="studio-modal-overlay active">
      <div className="studio-modal-card" style={{ width: '680px' }}>
        <div className="studio-modal-header">
          <div className="modal-header-icon" style={{ background: 'linear-gradient(135deg, var(--color-accent) 0%, var(--color-primary) 100%)' }}>
            <i className="fa-solid fa-shield-halved"></i>
          </div>
          <div>
            <h3 className="modal-header-title">Kiểm duyệt Kỹ năng nháp (AI Draft Approval)</h3>
            <p className="modal-header-desc">Duyệt và điều chỉnh các chỉ dẫn do AI tự động biên dịch trước khi xuất bản thành tệp cấu hình JSON.</p>
          </div>
          <button className="modal-close-btn" onClick={() => setSkillDraft(null)}>&times;</button>
        </div>
        
        <div className="studio-modal-body">
          <div className="modal-row">
            <div className="modal-col form-group">
              <label className="form-label">Tên định danh Kỹ năng</label>
              <input 
                type="text" 
                className="form-input" 
                style={{ fontFamily: 'var(--font-code)', fontSize: '13px' }} 
                value={skillDraft.name} 
                onChange={(e) => setSkillDraft(prev => ({ ...prev, name: e.target.value }))} 
              />
            </div>
            <div className="modal-col form-group">
              <label className="form-label">Mô tả tác vụ kỹ năng</label>
              <input 
                type="text" 
                className="form-input" 
                value={skillDraft.description} 
                onChange={(e) => setSkillDraft(prev => ({ ...prev, description: e.target.value }))} 
              />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Cấu hình System Prompt (Đã tối ưu hóa AI)</label>
            <textarea
              className="form-textarea"
              rows="6"
              style={{ 
                fontFamily: 'var(--font-code)', 
                fontSize: '11.5px', 
                background: 'rgba(0,0,0,0.3)', 
                border: '1px solid var(--border-glass)', 
                color: 'white', 
                padding: '10px' 
              }}
              value={skillDraft.system_prompt}
              onChange={(e) => setSkillDraft(prev => ({ ...prev, system_prompt: e.target.value }))}
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Phân quyền vai trò có thể gọi Kỹ năng (RBAC)</label>
            <div className="role-checkbox-group">
              <label className="role-checkbox-label">
                <input type="checkbox" defaultChecked />
                <span>ADMIN</span>
              </label>
              <label className="role-checkbox-label">
                <input type="checkbox" defaultChecked />
                <span>ACCOUNTANT</span>
              </label>
              <label className="role-checkbox-label">
                <input type="checkbox" />
                <span>EMPLOYEE</span>
              </label>
            </div>
          </div>
        </div>
        
        <div className="studio-modal-footer">
          <button className="modal-btn-secondary" onClick={() => setSkillDraft(null)}>Hủy bỏ nháp</button>
          <button 
            className="modal-btn-primary" 
            style={{ background: 'linear-gradient(135deg, var(--color-accent) 0%, var(--color-primary) 100%)' }} 
            onClick={handlePublish}
          >
            <i className="fa-solid fa-floppy-disk"></i>
            <span>Kích hoạt & Lưu trữ Skill</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default SkillDraftModal;
