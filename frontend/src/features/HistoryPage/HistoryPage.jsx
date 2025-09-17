import React, { useState, useEffect } from "react";
import Header from "../../components/Header";
import Panel from "../../components/Panel";
import Metric from "../../components/Metric";
import HistoryTab from "./HistoryTab/HistoryTab";
import { apiService, handleApiError } from "../../services/api_caller";
import { useNavigate } from "react-router-dom";
import AnalysisHistory from "./AnalysisHistory/AnalysisHistory";
import Button from "../../components/Button";
import "./HistoryPage.css";

const HistoryPage = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [showAnalysisDetail, setShowAnalysisDetail] = useState(false);

  const navigate = useNavigate();

  const panelButtons = ["AI Text Detector", "History"];

  const handlePanelSelect = (button) => {
    if (button === "AI Text Detector") {
      navigate("/AITextDetectorPage");
    }
  };

  const handleLogoClick = () => {
    setSelectedAnalysis(null);
    setShowAnalysisDetail(false);
    loadHistory();
  };

  const loadHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.getHistory();
      console.log("History response session ID:", response.data.session_id);
      console.log("History response:", response.data);
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

  const handleTabClick = (analysis) => {
    setSelectedAnalysis(analysis);
    setShowAnalysisDetail(true);
  };

  useEffect(() => {
    loadHistory();
  }, []);



  return (
    <div className="history-page">
      <Header onLogoClick={handleLogoClick} />
      
      <div className="main-content">
        <Panel buttons={panelButtons} onSelect={handlePanelSelect} />
        
        <div className="content-area">
          {showAnalysisDetail ? (
            // Show AnalysisHistory with Metrics
            <AnalysisHistory 
              analysis={selectedAnalysis}
              onBack={() => {
                setShowAnalysisDetail(false);
                setSelectedAnalysis(null);
              }}
            />
          ) : (
            // Show only the HistoryTab list (no Metrics)
            <div className="history-container-full">
              <h2 className="panel-title">Analysis History</h2>
              
              {error && (
                <div className="error-message">
                  {error}
                  <Button 
                    onClick={loadHistory}
                    variant="primary"
                    size="small"
                    style={{
                      marginLeft: '10px',
                    }}
                  >
                    Retry
                  </Button>
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
                    <Button 
                      onClick={clearHistory} 
                      variant="danger"
                      size="small"
                    >
                      Clear All History
                    </Button>
                  </div>

                  <div className="history-list">
                    {analyses.map((analysis, index) => (
                      <HistoryTab
                        key={analysis.id || index}
                        analysis={analysis}
                        onClick={handleTabClick}
                        isSelected={selectedAnalysis?.id === analysis.id}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;