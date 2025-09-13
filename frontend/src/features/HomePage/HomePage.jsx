import React from 'react';
import Button from "../../components/Button";
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

// Main homepage component with hero section and app preview
const HomePage = () => {
  const navigate = useNavigate();
  // Handle get started button click
  const handleGetStarted = () => {
    console.log('Get started clicked!');
    navigate("../AITextDetectorPage");
  };

  return (
    <div className="homepage">
      {/* Header with navigation */}
      <header className="homepage-header">
        <div className="logo">AICD</div>
        <nav className="nav">
          <a href="#contact" className="nav-link">Contact</a>
          <a href="#developers" className="nav-link">Developers</a>
        </nav>
      </header>

      {/* Main content area */}
      <main className="main-content">
        {/* Call-to-action section */}
        <section className="cta-section">
          <Button
            onClick={handleGetStarted}
          >
            Get Started
          </Button>
        </section>

        {/* App preview section */}
        <section className="app-preview">
          <img
            src="https://via.placeholder.com/1000x600/f8f9fa/6c757d?text=AICD+App+Preview"
            className="preview-image"
          />
        </section>
      </main>
    </div>
  );
};

export default HomePage;