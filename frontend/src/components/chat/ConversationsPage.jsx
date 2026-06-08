import React, { useState } from 'react';

function ConversationsPage({ conversations, onSelectConversation, onDeleteConversation, onStartChat }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartChat(input.trim());
    setInput('');
  };

  return (
    <div className="conv-page">
      <div className="conv-page-hero">
        <div className="conv-page-icon"><i className="fa-solid fa-brain"></i></div>
        <h2 className="conv-page-title">Trò chuyện Bot</h2>
        <p className="conv-page-sub">Bắt đầu cuộc trò chuyện mới hoặc tiếp tục từ lịch sử</p>
      </div>

      <form className="conv-page-input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          className="conv-page-input"
          placeholder="Nhập tin nhắn để bắt đầu cuộc trò chuyện mới..."
          value={input}
          onChange={e => setInput(e.target.value)}
          autoFocus
        />
        <button type="submit" className="conv-page-send">
          <i className="fa-solid fa-paper-plane"></i>
        </button>
      </form>

      {conversations.length > 0 && (
        <div className="conv-page-history">
          <span className="conv-page-history-title">Lịch sử trò chuyện</span>
          <div className="conv-page-list">
            {conversations.map(conv => (
              <div
                key={conv.id}
                className="conv-page-item"
                onClick={() => onSelectConversation(conv.id)}
              >
                <i className="fa-solid fa-message conv-page-item-icon"></i>
                <span className="conv-page-item-title">{conv.title || 'Cuộc trò chuyện'}</span>
                <button
                  className="conv-page-del"
                  title="Xóa"
                  onClick={e => { e.stopPropagation(); onDeleteConversation(conv.id); }}
                >
                  <i className="fa-solid fa-trash-can"></i>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ConversationsPage;
