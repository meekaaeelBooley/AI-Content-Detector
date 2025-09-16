import React, { useState } from "react";
import Header from "../../components/Header";
import Panel from "../../components/Panel";
import TextInput from "../../components/TextInput";
import Metric from "../../components/Metric";
import { apiService, handleApiError } from "../../services/api_caller"; 
import "./AITextDetectorPage.css";

const AITextDetectorPage = () => {
  const [selectedPanel, setSelectedPanel] = useState("AI Text Detector");
  const [aiScore, setAiScore] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  const panelButtons = ["AI Text Detector", "History"];

  const handlePanelSelect = (button) => {
    setSelectedPanel(button);
    if (button === "History") {
      // Navigate to the History page
      window.location.href = "/HistoryPage";
    } else {
      // Reset for AI Text Detector
      setAiScore(0);
      setError(null);
      setAnalysisResult(null);
    }
  };

  const handleTextSubmit = async (text) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await apiService.detectAI(text);
      const result = response.data;
      setAnalysisResult(result);
      
      // Extract AI probability from the result
      let aiProbability = 0;
      if (result.analysis_type === 'sentence_level') {
        aiProbability = result.result.overall_ai_probability * 100;
      } else {
        aiProbability = result.result.ai_probability * 100;
      }
      
      setAiScore(Math.round(aiProbability));
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error("API Error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileAttach = async (file) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await apiService.detectAIFile(file);
      const result = response.data;
      setAnalysisResult(result);
      
      // Extract AI probability from the result
      let aiProbability = 0;
      if (result.analysis_type === 'sentence_level') {
        aiProbability = result.result.overall_ai_probability * 100;
      } else {
        aiProbability = result.result.ai_probability * 100;
      }
      
      setAiScore(Math.round(aiProbability));
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error("API Error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLogoClick = () => {
    setSelectedPanel("AI Text Detector");
    setAiScore(0);
    setIsProcessing(false);
    setError(null);
    setAnalysisResult(null);
  };

  // Get confidence level description based on score
  const getConfidenceDescription = () => {
    if (!analysisResult) return "";
    
    if (aiScore >= 80) {
      return "High probability of AI-generated content";
    } else if (aiScore >= 60) {
      return "Moderate probability of AI-generated content";
    } else if (aiScore >= 40) {
      return "Mixed indicators - could be either AI or human";
    } else {
      return "High probability of human-written content";
    }
  };

  return (
    <div className="ai-text-detector-page">
      <Header onLogoClick={handleLogoClick} />
      
      <div className="main-content">
        {/* Panel on the left */}
        <Panel 
          buttons={panelButtons} 
          onSelect={handlePanelSelect} 
        />
        
        {/* Content area on the right (text input + metric) */}
        <div className="content-area">
          <div className="text-input-container">
            <h2 className="panel-title">{selectedPanel}</h2>
            <TextInput 
              onSubmit={handleTextSubmit}
              onFileAttach={handleFileAttach}
            />
            {error && (
              <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>
                {error}
              </div>
            )}
          </div>
          
          <div className="metric-container">
            <h3>AI Probability Score</h3>
            {isProcessing ? (
              <div className="processing-indicator">
                <div className="spinner" style={{
                  width: '40px',
                  height: '40px',
                  border: '4px solid #f3f3f3',
                  borderTop: '4px solid #8E12D5',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  margin: '0 auto'
                }}></div>
                <p>Analyzing content...</p>
              </div>
            ) : (
              <>
                <Metric percentage={aiScore} />
                <p className="metric-description">
                  {getConfidenceDescription()}
                </p>
                {analysisResult && (
                  <div style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                    <p>Analysis ID: {analysisResult.analysis_id}</p>
                    <p>Type: {analysisResult.analysis_type}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Add CSS for spinner animation */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default AITextDetectorPage;