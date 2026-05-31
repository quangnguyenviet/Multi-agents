import React from 'react';

// Basic Markdown / HTML formatting helper
const formatMarkdown = (text) => {
  if (!text) return "";
  let html = text;

  // Convert bullet points
  html = html.replace(/\* \*\*(.*?)\*\*: (.*?)(<br>|$)/g, '<li><strong>$1</strong>: $2</li>');
  html = html.replace(/\* (.*?)(<br>|$)/g, '<li>$1</li>');
  if (html.includes('<li>')) {
    html = html.replace(/(<li>.*?<\/li>)/gs, '<ul style="margin-left: 20px; margin-bottom: 10px;">$1</ul>');
  }

  // Convert bold styling
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  return html;
};

function MessageItem({ msg }) {
  const isUser = msg.role === 'user';
  const avatarText = isUser ? 'ME' : (msg.avatarAbbr || 'AG');

  return (
    <div className={`msg-row ${msg.role}`}>
      <div className="msg-avatar">{avatarText}</div>
      <div className="msg-content-wrapper">
        <div className="msg-bubble">
          {msg.routeInfoBadge && (
            <span className="skill-badge-tag" style={{ background: 'rgba(16, 185, 129, 0.12)', borderColor: 'rgba(16, 185, 129, 0.2)', color: '#a7f3d0', marginBottom: '8px', display: 'inline-flex' }}>
              <i className="fa-solid fa-route" style={{ marginRight: '6px' }}></i> {msg.routeInfoBadge}
            </span>
          )}
          {msg.skillTag && (
            <span className="skill-badge-tag" style={{ display: 'inline-flex', marginBottom: '8px' }}>
              <i className="fa-solid fa-tag" style={{ marginRight: '6px' }}></i> {msg.skillTag}
            </span>
          )}
          {(msg.routeInfoBadge || msg.skillTag) ? <br /> : null}
          <div dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.text) }} />
        </div>
        <div className="msg-meta">
          <span>{isUser ? 'Người dùng' : msg.agentName}</span> • <span>{msg.timestamp}</span>
        </div>
      </div>
    </div>
  );
}

export default MessageItem;
