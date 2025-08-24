import React, { useState } from "react";
import Header from "../../components/Header";
import Panel from "../../components/Panel";
import TextInput from "../../components/TextInput";
import Metric from "../../components/Metric";
import "./AITextDetectorPage.css";

/*
The main page component that orchestrates the AI text detection workflow, managing state for user input, processing, and detection results.
*/

const AITextDetectorPage = () => {
  const [selectedPanel, setSelectedPanel] = useState("AI Text Detector");
  const [aiScore, setAiScore] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const panelButtons = ["AI Text Detector"];

  /*
  Manages navigation between different detection features
  */
  const handlePanelSelect = (button) => {
    setSelectedPanel(button);
    setAiScore(0); // Reset score when switching panels
  };

  /*
  Processes text input and initiates AI analysis
  */
  const handleTextSubmit = (text) => {
    console.log("Text submitted:", text);
    setIsProcessing(true);
    
    // Simulate AI processing with timeout
    setTimeout(() => {
      const randomScore = Math.floor(Math.random() * 100);
      setAiScore(randomScore);
      setIsProcessing(false);
    }, 1500);
  };

  //Handles file uploads and validation
  const handleFileAttach = (file) => {
    console.log("File attached:", file.name);
    setIsProcessing(true);
    
    // Simulate file processing with longer timeout
    setTimeout(() => {
      const randomScore = Math.floor(Math.random() * 100);
      setAiScore(randomScore);
      setIsProcessing(false);
    }, 2000);
  };

  //Resets application state on logo click
  const handleLogoClick = () => {
    setSelectedPanel("AI Text Detector");
    setAiScore(0);
    setIsProcessing(false);
  };

  return (
    <div className="ai-text-detector-page">
      <Header onLogoClick={handleLogoClick} />
      
      <div className="main-content">
        <Panel 
          buttons={panelButtons} 
          onSelect={handlePanelSelect} 
        />
        
        <div className="content-area">
          <div className="text-input-container">
            <h2 className="panel-title">{selectedPanel}</h2>
            <TextInput 
              onSubmit={handleTextSubmit}
              onFileAttach={handleFileAttach}
            />
          </div>
          
          <div className="metric-container">
            <h3>AI Probability Score</h3>
            {isProcessing ? (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <p>Analyzing content...</p>
              </div>
            ) : (
              <Metric percentage={aiScore} />
            )}
            <p className="metric-description">
              {aiScore >= 70 
                ? "High probability of AI-generated content" 
                : aiScore >= 40 
                ? "Moderate probability of AI-generated content" 
                : "Low probability of AI-generated content"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AITextDetectorPage;