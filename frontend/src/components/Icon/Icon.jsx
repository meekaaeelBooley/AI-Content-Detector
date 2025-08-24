import React from 'react';
import './Icon.css';

// Flexible icon component that wraps react icons with custom styling
const Icon = ({
  icon: IconComponent, // React icon component passed as prop
  color = '#8E12D5', // Default purple color
  backgroundColor = 'white', // Default white background
  size = 40, // Default size in pixels
  isClickable = true, // Whether icon is interactive
  isDisabled = false, // Disabled state
  onClick, // Click handler function
  className = '', // Additional CSS classes
  ...props // Spread remaining props
}) => {
  // Handle click events with state validation
  const handleClick = (e) => {
    if (!isDisabled && isClickable && onClick) {
      onClick(e);
    }
  };

  // Dynamic styles based on props
  const iconStyles = {
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor: backgroundColor,
    borderRadius: '10px', // Slightly rounded corners
    cursor: isClickable && !isDisabled ? 'pointer' : 'default', // Pointer cursor for clickable icons
    opacity: isDisabled ? 0.5 : 1, // Visual feedback for disabled state
  };

  return (
    <div
      className={`icon-container ${className}`}
      style={iconStyles}
      onClick={handleClick}
      role={isClickable ? 'button' : 'presentation'} // ARIA role for accessibility
      aria-disabled={isDisabled} // Accessibility attribute
      tabIndex={isClickable && !isDisabled ? 0 : -1} // Keyboard tab navigation
      {...props} // Pass through any additional props
    >
      {/* Render the icon component if provided */}
      {IconComponent && (
        <IconComponent
          size={size * 0.6} // Scale icon to 60% of container size
          color={color}
          className="icon-svg"
        />
      )}
    </div>
  );
};

export default Icon;