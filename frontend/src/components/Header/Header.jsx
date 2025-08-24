import React from "react";
import "./Header.css";

// Simple header component with clickable logo
const Header = ({ onLogoClick }) => {
  return (
    <header className="header">
      <h1
        onClick={onLogoClick} // Click handler passed from parent component
        className="app-name"
      >
        AICD {/* Application name/logo */}
      </h1>
    </header>
  );
};

export default Header;