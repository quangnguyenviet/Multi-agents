import React, { useState } from 'react';

function AgentManager({ 
  activeTab, 
  agents, 
  saveSystemPrompt, 
  setAgentModalOpen 
}) {
  const [openPrompts, setOpenPrompts] = useState({});

  const togglePrompt = (key) => {
    setOpenPrompts(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className={`tab-content ${activeTab === 'tab-agents' ? 'active' : ''}`}>
      <div className="panel-header">
        <div className="panel-title-wrapper">
          <h2 className="panel-title">Thiết lập Đồ thị Multi-Agent (LangGraph)</h2>
          <p className="panel-desc">Cấu hình các nút Agent độc lập, tùy biến AI Instructions (System Prompt) và kết nối tức thì.</p>
        </div>
        <button className="panel-btn-primary" onClick={() => setAgentModalOpen(true)}>
          <i className="fa-solid fa-plus"></i>
          <span>Thêm mới Agent</span>
        </button>
      </div>

      <div className="agents-grid">
        {Object.keys(agents).map(key => {
          const agent = agents[key];
          const isPromptOpen = openPrompts[key];
          return (
            <div key={key} className="agent-mgmt-card">
              <div className="agent-mgmt-header">
                <div className="agent-mgmt-identity">
                  <div className="agent-mgmt-avatar">
                    <i className={`fa-solid ${agent.icon}`}></i>
                  </div>
                  <div className="agent-mgmt-name-wrap">
                    <h3 className="agent-mgmt-name">{agent.name}</h3>
                    <span className="agent-mgmt-id-badge">node_id: {key}</span>
                  </div>
                </div>
                
                <label className="switch-toggle-label">
                  <input type="checkbox" className="switch-input" defaultChecked />
                  <span className="switch-track"><span className="switch-thumb"></span></span>
                </label>
              </div>
              
              <p className="agent-mgmt-details">{agent.description}</p>
              
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '12px', marginTop: '4px' }}>
                <button 
                  className="modal-btn-secondary" 
                  style={{ 
                    fontSize: '11px', 
                    padding: '6px 12px', 
                    borderRadius: '6px', 
                    width: '100%', 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center' 
                  }} 
                  onClick={() => togglePrompt(key)}
                >
                  <span><i className="fa-solid fa-code" style={{ color: 'var(--color-primary)', marginRight: '6px' }}></i> Cấu hình System Prompt (AI Instructions)</span>
                  <i className={`fa-solid fa-chevron-down`} style={{ transition: 'transform 0.2s', transform: isPromptOpen ? 'rotate(180deg)' : 'rotate(0)' }}></i>
                </button>
                
                {isPromptOpen && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
                    <textarea
                      id={`prompt-textarea-${key}`}
                      className="form-textarea"
                      rows="4"
                      style={{ 
                        fontFamily: 'var(--font-code)', 
                        fontSize: '11.5px', 
                        background: 'rgba(0,0,0,0.3)', 
                        border: '1px solid var(--border-glass)', 
                        color: 'white', 
                        padding: '10px' 
                      }}
                      defaultValue={agent.system_prompt}
                    />
                    <button 
                      className="panel-btn-primary" 
                      style={{ alignSelf: 'flex-end', fontSize: '11px', padding: '6px 14px', borderRadius: '6px' }} 
                      onClick={() => {
                        const val = document.getElementById(`prompt-textarea-${key}`).value;
                        saveSystemPrompt(key, val);
                      }}
                    >
                      <i className="fa-solid fa-floppy-disk"></i> Lưu Prompt
                    </button>
                  </div>
                )}
              </div>

              <div className="agent-parameters-grid">
                <div className="slider-group">
                  <div className="slider-header">
                    <span className="slider-title">Temperature</span>
                    <span className="slider-value">0.2</span>
                  </div>
                  <input type="range" className="slider-input" min="0" max="1" step="0.1" defaultValue="0.2" />
                </div>
                <div className="select-group">
                  <span className="slider-title">Mô hình LLM nền</span>
                  <select className="mgmt-select-box" defaultValue="llama3-70b">
                    <option value="llama3-70b">Llama 3 (70B-Groq)</option>
                    <option value="gpt-4">GPT-4o (OpenAI)</option>
                    <option value="gemini-pro">Gemini 1.5 Pro</option>
                  </select>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AgentManager;
