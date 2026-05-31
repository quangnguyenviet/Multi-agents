import React, { useState } from 'react';

function ChatInputBar({ activeAgent, activeAgentName, onSendMessage }) {
  const [inputValue, setInputValue] = useState("");

  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSendMessage(inputValue);
    setInputValue("");
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const handleChipClick = (text) => {
    onSendMessage(text);
  };

  // Render quick shortcut chips based on active agent
  const renderShortcutChips = () => {
    if (activeAgent === 'hr_policies') {
      return (
        <>
          <div className="shortcut-chip" onClick={() => handleChipClick('Số ngày phép năm của tôi là bao nhiêu?')}>📅 Tra cứu ngày phép phép</div>
          <div className="shortcut-chip" onClick={() => handleChipClick('Thời gian làm việc hành chính?')}>⏱️ Giờ hành chính</div>
        </>
      );
    } else if (activeAgent === 'salary_management') {
      return (
        <>
          <div className="shortcut-chip" onClick={() => handleChipClick('Xem lương cá nhân của tôi')}>💵 Xem lương cá nhân</div>
          <div className="shortcut-chip" onClick={() => handleChipClick('Bảng lương tổng hợp toàn bộ nhân viên')}>📊 Xem bảng lương tổng</div>
        </>
      );
    } else if (activeAgent === 'system_admin') {
      return (
        <>
          <div className="shortcut-chip" onClick={() => handleChipClick('CPU và RAM máy chủ Dell?')}>💻 Thông số CPU & RAM</div>
          <div className="shortcut-chip" onClick={() => handleChipClick('Đọc danh sách nhân viên')}>📄 Tra cứu nhân sự công ty</div>
        </>
      );
    } else {
      return (
        <>
          <div className="shortcut-chip" onClick={() => handleChipClick('Mục tiêu hoạt động của bạn là gì?')}>❓ Mục tiêu hoạt động</div>
          <div className="shortcut-chip" onClick={() => handleChipClick('Hãy giới thiệu về các chỉ thị của bạn')}>ℹ️ Giới thiệu chỉ thị</div>
        </>
      );
    }
  };

  return (
    <div className="chat-input-bar-wrapper">
      <div className="shortcut-chips">
        {renderShortcutChips()}
      </div>
      <div className="chat-input-box">
        <input
          type="text"
          className="chat-input"
          placeholder={`Hỏi ${activeAgentName || 'Agent'}...`}
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
