import React from 'react';

function SwitchToggle({ checked, onChange, defaultChecked }) {
  return (
    <label className="switch-toggle-label">
      <input 
        type="checkbox" 
        className="switch-input" 
        checked={checked} 
        onChange={onChange} 
        defaultChecked={defaultChecked}
      />
      <span className="switch-track">
        <span className="switch-thumb"></span>
      </span>
    </label>
  );
}

export default SwitchToggle;
