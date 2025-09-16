import React, { useState, useEffect } from "react";
import Header from "../../components/Header";
import Panel from "../../components/Panel";
import Metric from "../../components/Metric";
import { apiService, handleApiError } from "../../services/api_caller";
import "./HistoryPage.css";

const HistoryPage = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const panelButtons = ["AI Text Detector", "History"];

  const handlePanelSelect = (button) => {
    if (button === "AI Text Detector") {
      // Navigate to the AI Text Detector page
      window.location.href = "/AITextDetectorPage";
    }
  };

  const handleLogoClick = () => {
    setSelectedAnalysis(null);
    loadHistory();
  };

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getHistory();
      setAnalyses(response.data.analyses || []);
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error("Error loading history:", err);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (window.confirm("Are you sure you want to clear all history?")) {
      try {
        await apiService.clearHistory();
        setAnalyses([]);
        setSelectedAnalysis(null);
      } catch (err) {
        const errorMessage = handleApiError(err);
        setError(errorMessage);
        console.error("Error clearing history:", err);
      }
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getAIScore = (analysis) => {
    if (analysis.analysis_type === 'sentence_level') {
      return Math.round(analysis.overall_result?.overall_ai_probability * 100);
    } else {
      return Math.round(analysis.result?.ai_probability * 100);
    }
  };

  return (
    <div className="history-page">
      <Header onLogoClick={handleLogoClick} />
      
      <div className="main-content">
        <Panel buttons={panelButtons} onSelect={handlePanelSelect} />
        
        <div className="content-area">
          <div className="history-container">
            <h2 className="panel-title">Analysis History</h2>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {loading ? (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>Loading history...</p>
              </div>
            ) : analyses.length === 0 ? (
              <div className="empty-state">
                <p>No analysis history yet.</p>
                <p>Go to AI Text Detector to analyze some text!</p>
              </div>
            ) : (
              <>
                <div className="history-controls">
                  <button onClick={clearHistory} className="clear-button">
                    Clear All History
                  </button>
                </div>

                <div className="history-list">
                  {analyses.map((analysis, index) => (
                    <div
                      key={analysis.id || index}
                      className={`history-item ${
                        selectedAnalysis?.id === analysis.id ? "selected" : ""
                      }`}
                      onClick={() => setSelectedAnalysis(analysis)}
                    >
                      <div className="item-preview">
                        <h4>
                          {analysis.filename || "Text Analysis"}
                        </h4>
                        <p className="preview-text">
                          {analysis.text_preview?.substring(0, 100)}
                          {analysis.text_preview?.length > 100 ? "..." : ""}
                        </p>
                        <div className="item-meta">
                          <span className="score">
                            AI Score: {getAIScore(analysis)}%
                          </span>
                          <span className="date">
                            {formatDate(analysis.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
          
          <div className="metric-container">
            <h3>Selected Analysis</h3>
            {selectedAnalysis ? (
              <>
                <Metric percentage={getAIScore(selectedAnalysis)} />
                <div className="analysis-details">
                  <p><strong>Type:</strong> {selectedAnalysis.source_type}</p>
                  {selectedAnalysis.filename && (
                    <p><strong>File:</strong> {selectedAnalysis.filename}</p>
                  )}
                  <p><strong>Date:</strong> {formatDate(selectedAnalysis.timestamp)}</p>
                  <p><strong>Text Length:</strong> {selectedAnalysis.text_length} characters</p>
                  <p><strong>Analysis Type:</strong> {selectedAnalysis.analysis_type}</p>
                </div>
              </>
            ) : (
              <div className="no-selection">
                <p>Select an analysis from the list to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;