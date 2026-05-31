import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';

function MessageList({ chatMessages, isTyping }) {
  const messageListEndRef = useRef(null);

  // Auto-scroll to bottom of message list on new messages or typing indicator status changes
  useEffect(() => {
    messageListEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isTyping]);

  return (
    <div className="message-list">
      {chatMessages.map((msg, idx) => (
        <MessageItem key={idx} msg={msg} />
      ))}
      
      {isTyping && (
        <div className="msg-row assistant">
          <div className="msg-avatar">AG</div>
          <div className="msg-content-wrapper">
            <div className="msg-bubble" style={{ color: 'var(--text-muted)' }}>
              <i className="fa-solid fa-circle-notch fa-spin"></i> Agent đang suy nghĩ...
            </div>
          </div>
        </div>
      )}
      
      <div ref={messageListEndRef} />
    </div>
  );
}

export default MessageList;
