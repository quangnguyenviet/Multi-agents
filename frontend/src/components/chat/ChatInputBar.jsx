import React, { useState, useRef } from 'react';

function ChatInputBar({ onSendMessage }) {
  const [inputValue, setInputValue] = useState("");
  const [attachedFile, setAttachedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleSend = () => {
    if (!inputValue.trim() && !attachedFile) return;
    onSendMessage(inputValue, attachedFile);
    setInputValue("");
    setAttachedFile(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handleChipClick = (text) => {
    onSendMessage(text, null);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) setAttachedFile(file);
    e.target.value = "";
  };

  return (
    <div className="chat-input-bar-wrapper">
      <div className="shortcut-chips">
        <div className="shortcut-chip" onClick={() => handleChipClick('Bạn có thể giúp tôi điều gì?')}>❓ Bạn có thể giúp gì?</div>
        <div className="shortcut-chip" onClick={() => handleChipClick('Hãy giới thiệu về bản thân bạn')}>ℹ️ Giới thiệu</div>
        <div className="shortcut-chip" onClick={() => handleChipClick('Tóm tắt những điều bạn có thể làm')}>📋 Tóm tắt khả năng</div>
      </div>

      {attachedFile && (
        <div className="attached-file-badge">
          <span>📄 {attachedFile.name}</span>
          <button className="remove-file-btn" onClick={() => setAttachedFile(null)}>✕</button>
        </div>
      )}

      <div className="chat-input-box">
        <input
          type="file"
          accept=".pdf"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <button
          className="chat-attach-btn"
          title="Đính kèm PDF"
          onClick={() => fileInputRef.current.click()}
        >
          <i className="fa-solid fa-paperclip"></i>
        </button>
        <input
          type="text"
          className="chat-input"
          placeholder={attachedFile ? "Nhập yêu cầu cho file CV..." : "Nhập câu hỏi của bạn..."}
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
