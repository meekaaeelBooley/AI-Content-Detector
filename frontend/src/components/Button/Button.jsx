import React, { useState } from 'react';
import './Button.css';

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary',
  size = 'medium',
  borderRadius = '100px',
  color,
  backgroundColor,
  disabled = false,
  ...props 
}) => {
  const [isClicked, setIsClicked] = useState(false);

  const handleClick = (e) => {
    if (disabled) return;
    
    setIsClicked(true);
    setTimeout(() => setIsClicked(false), 150);
    if (onClick) onClick(e);
  };

  // Determine button classes based on props
  const buttonClasses = [
    'custom-button',
    variant,
    size,
    isClicked ? 'clicked' : '',
    disabled ? 'disabled' : ''
  ].filter(Boolean).join(' ');

  // Custom styles based on props
  const customStyles = {
    borderRadius: borderRadius,
    ...(color && { color }),
    ...(backgroundColor && { backgroundColor })
  };

  return (
    <button
      className={buttonClasses}
      style={customStyles}
      onClick={handleClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;