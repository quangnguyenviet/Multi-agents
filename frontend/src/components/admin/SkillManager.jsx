import React, { useState } from 'react';
import SwitchToggle from '../common/SwitchToggle';

function SkillManager({ 
  activeTab, 
  skills, 
  agents, 
  deleteSkill, 
  onStartSkillDraft 
}) {
  const [newSkillInput, setNewSkillInput] = useState({ 
    name: "get_company_employee_list", 
    description: "Lấy danh sách tất cả nhân viên trong hệ thống và hiển thị dạng bảng chuyên nghiệp", 
    agent: "system_admin" 
  });

  const handleCreateDraft = () => {
    if (!newSkillInput.name.trim() || !newSkillInput.description.trim()) {
      alert("Vui lòng nhập tên và mô tả kỹ năng!");
      return;
    }
    onStartSkillDraft(newSkillInput.name, newSkillInput.description, newSkillInput.agent);
  };

  return (
    <div className={`tab-content ${activeTab === 'tab-skills' ? 'active' : ''}`}>
      <div className="panel-header">
        <div className="panel-title-wrapper">
          <h2 className="panel-title">Skill Studio (Human-in-the-loop)</h2>
          <p className="panel-desc">Thiết kế kỹ năng mới bằng ngôn ngữ tự nhiên. AI sẽ tự động sinh mã cấu hình JSON để bạn review trước khi biên dịch.</p>
        </div>
        
        <div className="panel-header-buttons">
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              placeholder="Tên kỹ năng..."
              className="form-input"
              style={{ width: '160px', padding: '6px 12px', fontSize: '12px' }}
              value={newSkillInput.name}
              onChange={(e) => setNewSkillInput(prev => ({ ...prev, name: e.target.value }))}
            />
            <input
              type="text"
              placeholder="Mô tả kỹ năng nháp bằng tiếng Việt..."
              className="form-input"
              style={{ width: '280px', padding: '6px 12px', fontSize: '12px' }}
              value={newSkillInput.description}
              onChange={(e) => setNewSkillInput(prev => ({ ...prev, description: e.target.value }))}
            />
            <select
              className="form-select"
              style={{ padding: '6px 12px', fontSize: '12px' }}
              value={newSkillInput.agent}
              onChange={(e) => setNewSkillInput(prev => ({ ...prev, agent: e.target.value }))}
            >
              {Object.keys(agents).filter(k => k !== 'auto_route').map(k => (
                <option key={k} value={k}>{agents[k].name}</option>
              ))}
            </select>
          </div>
          
          <button className="panel-btn-primary" onClick={handleCreateDraft}>
            <i className="fa-solid fa-wand-magic-sparkles"></i>
            <span>Tạo Kỹ năng (AI Draft)</span>
          </button>
        </div>
      </div>

      <div className="skills-grid-view">
        {skills.map(skill => (
          <div key={skill.id} className="skill-mgmt-card">
            <div className="skill-mgmt-title-row">
              <div>
                <h3 className="skill-mgmt-name">{skill.name}</h3>
                <span className="skill-mgmt-badge">{skill.category}</span>
              </div>
              
              <SwitchToggle defaultChecked={skill.active} />
            </div>
            
            <p className="skill-mgmt-desc">{skill.description}</p>
            
            <div className="skill-mgmt-footer">
              <span className="skill-mgmt-agent-badge">
                <i className="fa-solid fa-robot"></i> {agents[skill.agent]?.name || skill.agent}
              </span>
              
              <div className="skill-mgmt-actions">
                <button className="skill-action-icon-btn" title="Chỉnh sửa"><i className="fa-solid fa-pen-to-square"></i></button>
                <button className="skill-action-icon-btn delete-btn" title="Xóa" onClick={() => deleteSkill(skill.id)}><i className="fa-solid fa-trash-can"></i></button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SkillManager;
