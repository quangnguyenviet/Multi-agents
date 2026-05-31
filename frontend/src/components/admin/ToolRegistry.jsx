import React from 'react';
import SwitchToggle from '../common/SwitchToggle';

function ToolRegistry({ 
  activeTab, 
  tools, 
  agents, 
  toggleToolStatus, 
  deleteTool, 
  setToolModalOpen 
}) {
  return (
    <div className={`tab-content ${activeTab === 'tab-tools' ? 'active' : ''}`}>
      <div className="panel-header">
        <div className="panel-title-wrapper">
          <h2 className="panel-title">Tool Registry & Config (Công cụ gọi ngoài)</h2>
          <p className="panel-desc">Đăng ký schemas, định danh API và thiết lập liên kết gọi công cụ tự động dành cho các Agent chuyên trách.</p>
        </div>
        <button 
          className="panel-btn-primary" 
          style={{ background: 'linear-gradient(135deg, var(--color-accent) 0%, var(--color-primary) 100%)' }} 
          onClick={() => setToolModalOpen(true)}
        >
          <i className="fa-solid fa-screwdriver-wrench"></i>
          <span>Đăng ký Tool mới</span>
        </button>
      </div>

      <div className="skills-grid-view">
        {tools.map(tool => (
          <div key={tool.id} className="skill-mgmt-card">
            <div className="skill-mgmt-title-row">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <div style={{ 
                    width: '28px', 
                    height: '28px', 
                    borderRadius: '6px', 
                    background: 'rgba(99, 102, 241, 0.1)', 
                    border: '1px solid rgba(99, 102, 241, 0.2)', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    color: 'var(--color-primary)' 
                  }}>
                    <i className={`fa-solid ${tool.icon}`} style={{ alignSelf: 'center' }}></i>
                  </div>
                  <h3 className="skill-mgmt-name" style={{ margin: 0 }}>{tool.name}</h3>
                </div>
                <span className="skill-mgmt-badge">{tool.category}</span>
              </div>
              
              <SwitchToggle 
                checked={tool.active} 
                onChange={() => toggleToolStatus(tool.id)} 
              />
            </div>
            
            <p className="skill-mgmt-desc">{tool.description}</p>
            
            <div className="skill-mgmt-footer">
              <span className="skill-mgmt-agent-badge" style={{ color: 'var(--color-accent)' }}>
                <i className="fa-solid fa-robot"></i> {agents[tool.agent]?.name || "Không gán (Chung)"}
              </span>
              
              <div className="skill-mgmt-actions">
                <button className="skill-action-icon-btn" title="Chỉnh sửa"><i className="fa-solid fa-pen-to-square"></i></button>
                <button className="skill-action-icon-btn delete-btn" title="Xóa" onClick={() => deleteTool(tool.id)}><i className="fa-solid fa-trash-can"></i></button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ToolRegistry;
