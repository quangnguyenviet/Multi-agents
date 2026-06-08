import React from 'react';

const applyInline = (text) =>
  text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code style="background:rgba(99,102,241,0.15);padding:1px 5px;border-radius:3px;font-family:monospace;font-size:12px;">$1</code>');

const formatMarkdown = (text) => {
  if (!text) return "";

  const lines = text.split('\n');
  const out = [];
  let inUl = false;
  let inOl = false;

  const closeList = () => {
    if (inUl) { out.push('</ul>'); inUl = false; }
    if (inOl) { out.push('</ol>'); inOl = false; }
  };

  for (const line of lines) {
    if (line.startsWith('### ')) {
      closeList();
      out.push(`<h3 style="font-size:14px;font-weight:700;margin:10px 0 3px;color:#c7d2fe;">${applyInline(line.slice(4))}</h3>`);
    } else if (line.startsWith('## ')) {
      closeList();
      out.push(`<h2 style="font-size:15px;font-weight:700;margin:12px 0 4px;color:#c7d2fe;">${applyInline(line.slice(3))}</h2>`);
    } else if (line.startsWith('# ')) {
      closeList();
      out.push(`<h1 style="font-size:16px;font-weight:700;margin:14px 0 4px;color:#e0e7ff;">${applyInline(line.slice(2))}</h1>`);
    } else if (/^---+$/.test(line.trim())) {
      closeList();
      out.push('<hr style="border:none;border-top:1px solid rgba(99,102,241,0.3);margin:10px 0;" />');
    } else if (/^[-*] /.test(line)) {
      if (inOl) { out.push('</ol>'); inOl = false; }
      if (!inUl) { out.push('<ul style="margin:4px 0 8px 18px;padding:0;">'); inUl = true; }
      out.push(`<li>${applyInline(line.slice(2))}</li>`);
    } else if (/^\d+\. /.test(line)) {
      if (inUl) { out.push('</ul>'); inUl = false; }
      if (!inOl) { out.push('<ol style="margin:4px 0 8px 18px;padding:0;">'); inOl = true; }
      out.push(`<li>${applyInline(line.replace(/^\d+\. /, ''))}</li>`);
    } else {
      closeList();
      out.push(line.trim() === '' ? '<br>' : `<p style="margin:2px 0;">${applyInline(line)}</p>`);
    }
  }

  closeList();
  return out.join('');
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

        {msg.wordDownloadUrl && (
          <div className="word-download-card">
            <i className="fa-solid fa-file-word" style={{ marginRight: '8px', fontSize: '18px' }}></i>
            <span style={{ flex: 1 }}>File CV Word đã sẵn sàng</span>
            <a href={msg.wordDownloadUrl} download className="word-download-btn">
              <i className="fa-solid fa-download" style={{ marginRight: '6px' }}></i>Tải về (.docx)
            </a>
          </div>
        )}

        <div className="msg-meta">
          <span>{isUser ? 'Người dùng' : msg.agentName}</span> • <span>{msg.timestamp}</span>
        </div>
      </div>
    </div>
  );
}

export default MessageItem;
