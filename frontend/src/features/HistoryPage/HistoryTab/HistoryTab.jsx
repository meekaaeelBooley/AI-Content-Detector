import React from "react";
import "./HistoryTab.css";

const HistoryTab = ({ 
  analysis, 
  onClick, 
  isSelected = false 
}) => {
  const {
    text_preview,
    timestamp,
    filename,
    analysis_type,
    overall_result,  // This is where the data actually is
    result           // For single_text analysis type
  } = analysis;

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getAIScore = () => {
    if (analysis_type === 'sentence_level') {
      // For sentence-level analysis, use overall_result
      return Math.round((overall_result?.overall_ai_probability || 0) * 100);
    } else {
      // For single text analysis, use result
      return Math.round((result?.ai_probability || 0) * 100);
    }
  };

  const getPreviewText = () => {
    if (filename) {
      return filename;
    }
    
    const text = text_preview || "";
    const words = text.split(' ');
    if (words.length <= 8) {
      return text;
    }
    return words.slice(0, 8).join(' ') + '...';
  };

  const getClassification = () => {
    const aiScore = getAIScore();
    return aiScore > 50 ? "AI-generated" : "Human-written";
  };

  return (
    <div 
      className={`history-tab ${isSelected ? "selected" : ""}`}
      onClick={() => onClick(analysis)}
    >
      <div className="tab-content">
        <h4 className="tab-title">
          {filename ? "File Analysis" : "Text Analysis"}
        </h4>
        <p className="tab-preview">
          {getPreviewText()}
        </p>
        <div className="tab-meta">
          <span className="tab-score">
            AI: {getAIScore()}%
          </span>
          <span className="tab-date">
            {formatDate(timestamp)}
          </span>
        </div>
        <div className="tab-classification">
          {getClassification()}
        </div>
      </div>
    </div>
  );
};

export default HistoryTab;