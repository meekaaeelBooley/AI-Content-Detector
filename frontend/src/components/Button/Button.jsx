import React, { useState } from 'react';
import './Button.css';

// Reusable button component with click animation feedback
const Button = ({ children, onClick, ...props }) => {
  // State to track if button is currently clicked for visual feedback
  const [isClicked, setIsClicked] = useState(false);

  // Enhanced click handler that triggers visual feedback
  const handleClick = (e) => {
    setIsClicked(true);
    setTimeout(() => setIsClicked(false), 150); // Brief animation duration
    if (onClick) onClick(e); // Propagate original onClick event
  };

  return (
    <button
      className={`custom-button ${isClicked ? 'clicked' : ''}`} // Apply clicked class during animation
      onClick={handleClick}
      {...props} // Pass through any additional props (disabled, type, etc.)
    >
      {children} {/* Render button content */}
    </button>
  );
};

export default Button;