import React, { useState } from "react";

// Side panel navigation component with selectable buttons
const Panel = ({ buttons = [], onSelect }) => {
  // Track currently selected button
  const [selected, setSelected] = useState(null);

  // Handle button selection and callback
  const handleClick = (button) => {
    setSelected(button);
    if (onSelect) onSelect(button); // Notify parent component of selection
  };

  return (
    <aside
      style={{
        backgroundColor: "#F0F7FB", // Light blue background
        width: "200px", // Fixed sidebar width
        height: "100vh", // Full viewport height
        display: "flex",
        flexDirection: "column", // Stack buttons vertically
        padding: "1rem",
        boxShadow: "2px 0 4px rgba(0,0,0,0.05)" // Right side shadow
      }}
    >
      {/* Map through button labels to create navigation items */}
      {buttons.map((btn) => (
        <button
          key={btn}
          onClick={() => handleClick(btn)}
          style={{
            backgroundColor: selected === btn ? "#6A0BA8" : "#8E12D5", // Darker purple for selected
            color: "white",
            border: "none",
            borderRadius: "4px",
            padding: "0.75rem 1rem",
            marginBottom: "0.5rem", // Spacing between buttons
            cursor: "pointer",
            textAlign: "left", // Left-aligned text
            fontSize: "1rem",
          }}
        >
          {btn}
        </button>
      ))}
    </aside>
  );
};

export default Panel;