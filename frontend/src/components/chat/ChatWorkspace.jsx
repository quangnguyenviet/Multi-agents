import React from 'react';
import MessageList from './MessageList';
import ChatInputBar from './ChatInputBar';

function ChatWorkspace({ 
  activeTab, 
  activeAgent, 
  setActiveAgent, 
  agents, 
  chatMessages, 
  isTyping, 
  handleSendMessage 
}) {
  const currentAgent = agents[activeAgent] || {};

  return (
    <div className={`tab-content ${activeTab === 'tab-chat' ? 'active' : ''}`}>
      <div className="chat-header">
        <div className="agent-selector-bar">
          <div className="header-agent-avatar">
            <i className={`fa-solid ${currentAgent.icon || 'fa-route'}`}></i>
          </div>
          <div className="header-agent-meta">
            <span className="header-agent-title">{currentAgent.name}</span>
            <span className="header-agent-status">
              <span className="status-dot"></span> Đang hoạt động
            </span>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Cấu hình Agent:</span>
          <select className="chat-agent-dropdown" value={activeAgent} onChange={(e) => setActiveAgent(e.target.value)}>
            {Object.keys(agents).map(key => (
              <option key={key} value={key}>{agents[key].name}</option>
            ))}
          </select>
        </div>
      </div>

      <MessageList chatMessages={chatMessages} isTyping={isTyping} />

      <ChatInputBar 
        activeAgent={activeAgent} 
        activeAgentName={currentAgent.name} 
        onSendMessage={handleSendMessage} 
      />
    </div>
  );
}

export default ChatWorkspace;
