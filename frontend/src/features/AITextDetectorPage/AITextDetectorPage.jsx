import React, { useState, useEffect } from "react";
import Header from "../../components/Header";
import Panel from "../../components/Panel";
import TextInput from "../../components/TextInput";
import Metric from "../../components/Metric";
import { apiService, handleApiError } from "../../services/api_caller"; 
import { useNavigate } from "react-router-dom";
import "./AITextDetectorPage.css";

const AITextDetectorPage = () => {
  const [selectedPanel, setSelectedPanel] = useState("AI Text Detector");
  const [aiScore, setAiScore] = useState(0);
  const [confidenceScore, setConfidenceScore] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const navigate = useNavigate();

  const panelButtons = ["AI Text Detector", "History"];

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await apiService.getSessionInfo();
        console.log("Session info:", response.data);
      } catch (err) {
        console.log("No active session or session check failed");
      }
    };
    
    checkSession();
  }, []);

  const handlePanelSelect = (button) => {
    if (button === "History") {
      navigate("/HistoryPage");
    } else {
      setAiScore(0);
      setConfidenceScore(0);
      setError(null);
      setAnalysisResult(null);
    }
  };

  const refreshHistory = async () => {
    try {
      await apiService.getHistory();
      console.log("History refreshed - session maintained");
    } catch (err) {
      console.log("History refresh optional - session maintained by cookie");
    }
  };

  const handleTextSubmit = async (text) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await apiService.detectAI(text);
      const result = response.data;
      setAnalysisResult(result);
      
      console.log("Analysis session ID:", result.session_id);
      
      // Extract AI probability and confidence from the result
      let aiProbability = 0;
      let confidence = 0;
      
      if (result.analysis_type === 'sentence_level') {
        aiProbability = result.result.overall_ai_probability * 100;
        confidence = result.result.overall_confidence * 100;
      } else {
        aiProbability = result.result.ai_probability * 100;
        confidence = result.result.confidence * 100;
      }
      
      setAiScore(Math.round(aiProbability));
      setConfidenceScore(Math.round(confidence));
      
      await refreshHistory();
      
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
      
      let aiProbability = 0;
      let confidence = 0;
      
      if (result.analysis_type === 'sentence_level') {
        aiProbability = result.result.overall_ai_probability * 100;
        confidence = result.result.overall_confidence * 100;
      } else {
        aiProbability = result.result.ai_probability * 100;
        confidence = result.result.confidence * 100;
      }
      
      setAiScore(Math.round(aiProbability));
      setConfidenceScore(Math.round(confidence));
      
      await refreshHistory();
      
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error("File Upload Error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLogoClick = () => {
    setSelectedPanel("AI Text Detector");
    setAiScore(0);
    setConfidenceScore(0);
    setIsProcessing(false);
    setError(null);
    setAnalysisResult(null);
  };

  const getConfidenceDescription = () => {
    if (!analysisResult) return "Submit text to analyze";
    
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

  const getConfidenceLevel = () => {
    if (!analysisResult) return "N/A";
    
    if (confidenceScore >= 90) {
      return "Very High";
    } else if (confidenceScore >= 75) {
      return "High";
    } else if (confidenceScore >= 60) {
      return "Moderate";
    } else {
      return "Low";
    }
  };

return (
    <div className="ai-text-detector-page">
      <Header onLogoClick={handleLogoClick} />
      
      <div className="main-content">
        <div className="panel-container">
          <Panel 
            buttons={panelButtons} 
            onSelect={handlePanelSelect} 
          />
        </div>
        
        <div className="content-area">
          <div className="text-input-container">
            <h2 className="panel-title">{selectedPanel}</h2>
            <TextInput 
              onSubmit={handleTextSubmit}
              onFileAttach={handleFileAttach}
            />
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
          
          <div className="metric-container">
            <h3>Analysis Results</h3>
            {isProcessing ? (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <p>Analyzing content...</p>
              </div>
            ) : (
              <div className="metrics-stack">
                <div className="metric-item">
                  <h4>AI Probability</h4>
                  <Metric percentage={aiScore} />
                  <p className="metric-description">
                    {getConfidenceDescription()}
                  </p>
                </div>
                
                <div className="metric-item">
                  <h4>Confidence</h4>
                  <Metric 
                    percentage={confidenceScore} 
                    strokeColor="#28a745" // Green for confidence
                  />
                  <p className="metric-description">
                    {getConfidenceLevel()} confidence
                  </p>
                </div>
                
                {analysisResult && (
                  <div className="analysis-details">
                    <p><strong>Analysis ID:</strong> {analysisResult.analysis_id}</p>
                    <p><strong>Type:</strong> {analysisResult.analysis_type}</p>
                    <p><strong>Session:</strong> {analysisResult.session_id?.substring(0, 8)}...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AITextDetectorPage;