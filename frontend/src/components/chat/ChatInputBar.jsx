import React, { useState } from 'react';

function ChatInputBar({ onSendMessage }) {
  const [inputValue, setInputValue] = useState("");

  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSendMessage(inputValue);
    setInputValue("");
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handleChipClick = (text) => {
    onSendMessage(text);
  };

  return (
    <div className="chat-input-bar-wrapper">
      <div className="shortcut-chips">
        <div className="shortcut-chip" onClick={() => handleChipClick('Bạn có thể giúp tôi điều gì?')}>❓ Bạn có thể giúp gì?</div>
        <div className="shortcut-chip" onClick={() => handleChipClick('Hãy giới thiệu về bản thân bạn')}>ℹ️ Giới thiệu</div>
        <div className="shortcut-chip" onClick={() => handleChipClick('Tóm tắt những điều bạn có thể làm')}>📋 Tóm tắt khả năng</div>
      </div>
      <div className="chat-input-box">
        <input
          type="text"
          className="chat-input"
          placeholder="Nhập câu hỏi của bạn..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="chat-send-btn" onClick={handleSend}>
          <i className="fa-solid fa-paper-plane"></i>
        </button>
      </div>
    </div>
  );
}

export default ChatInputBar;
