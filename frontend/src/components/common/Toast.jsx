import React from 'react';

function Toast({ active, message }) {
  return (
    <div className={`toast-notification ${active ? 'active' : ''}`}>
      <i className="fa-solid fa-circle-check" style={{ fontSize: '18px' }}></i>
      <span>{message}</span>
    </div>
  );
}

export default Toast;
