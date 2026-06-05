import React from 'react';
import MessageList from './MessageList';
import ChatInputBar from './ChatInputBar';

function ChatWorkspace({ chatMessages, isTyping, handleSendMessage }) {
  return (
    <div className="tab-content active">
      <div className="chat-header">
        <div className="agent-selector-bar">
          <div className="header-agent-avatar">
            <i className="fa-solid fa-brain"></i>
          </div>
          <div className="header-agent-meta">
            <span className="header-agent-title">AI Assistant</span>
            <span className="header-agent-status">
              <span className="status-dot"></span> Đang hoạt động
            </span>
          </div>
        </div>
      </div>

      <MessageList chatMessages={chatMessages} isTyping={isTyping} />

      <ChatInputBar onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatWorkspace;
