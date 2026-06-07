import React from 'react';

function ToolRegistry({ activeTab, tools }) {
  return (
    <div className={`tab-content ${activeTab === 'tab-tools' ? 'active' : ''}`}>
      <div className="panel-header">
        <div className="panel-title-wrapper">
          <h2 className="panel-title">Tool Registry (Công cụ hệ thống)</h2>
          <p className="panel-desc">
            Danh sách các tool Python được bind vào LLM. Thêm tool mới = viết function trong <code>backend/tools/</code>.
          </p>
        </div>
        <div style={{
          padding: '6px 14px',
          borderRadius: '8px',
          background: 'rgba(99,102,241,0.08)',
          border: '1px solid rgba(99,102,241,0.2)',
          color: 'var(--color-primary)',
          fontSize: '13px',
          fontFamily: 'monospace',
        }}>
          <i className="fa-solid fa-code" style={{ marginRight: '6px' }}></i>
          {tools.length} tools active
        </div>
      </div>

      <div className="skills-grid-view">
        {tools.map(tool => (
          <div key={tool.id} className="skill-mgmt-card">
            <div className="skill-mgmt-title-row">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                  flexShrink: 0,
                }}>
                  <i className="fa-solid fa-wrench" style={{ fontSize: '13px' }}></i>
                </div>
                <div>
                  <h3 className="skill-mgmt-name" style={{ margin: 0, fontFamily: 'monospace', fontSize: '13px' }}>
                    {tool.name}
                  </h3>
                </div>
              </div>

              <span style={{
                padding: '3px 10px',
                borderRadius: '20px',
                fontSize: '11px',
                fontWeight: 600,
                background: 'rgba(34,197,94,0.1)',
                color: '#22c55e',
                border: '1px solid rgba(34,197,94,0.2)',
                whiteSpace: 'nowrap',
              }}>
                <i className="fa-solid fa-circle" style={{ fontSize: '7px', marginRight: '5px' }}></i>
                Active
              </span>
            </div>

            <p className="skill-mgmt-desc" style={{ marginTop: '10px' }}>
              {tool.description}
            </p>

            <div className="skill-mgmt-footer" style={{ marginTop: '8px' }}>
              <span className="skill-mgmt-badge">
                <i className="fa-solid fa-python" style={{ marginRight: '4px' }}></i>
                System Tool
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ToolRegistry;
