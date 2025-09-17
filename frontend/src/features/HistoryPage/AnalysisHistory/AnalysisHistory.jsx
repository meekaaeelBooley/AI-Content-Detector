import React from "react";
import Metric from "../../../components/Metric";
import "./AnalysisHistory.css";

const AnalysisHistory = ({ analysis, onBack }) => {
  if (!analysis) {
    return (
      <div className="analysis-history">
        <div className="no-analysis-selected">
          <p>No analysis selected</p>
          <button onClick={onBack} className="back-button">
            Back to History
          </button>
        </div>
      </div>
    );
  }

  const {
    text_preview,
    timestamp,
    filename,
    analysis_type,
    source_type,
    text_length,
    overall_result,
    result,
    sentence_analysis
  } = analysis;

  const getAIScore = () => {
    if (analysis_type === 'sentence_level') {
      return Math.round((overall_result?.overall_ai_probability || 0) * 100);
    } else {
      return Math.round((result?.ai_probability || 0) * 100);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getFullText = () => {
    if (sentence_analysis) {
      return sentence_analysis.map(item => item.sentence).join(' ');
    }
    return text_preview || "Full text not available";
  };

  const renderHighlightedText = () => {
    if (analysis_type !== 'sentence_level' || !sentence_analysis) {
      return <div className="text-content">{getFullText()}</div>;
    }

    return (
      <div className="text-content">
        {sentence_analysis.map((sentence, index) => (
          <span
            key={index}
            className={`sentence-highlight ${
              sentence.result.classification.toLowerCase() === 'ai-generated' 
                ? 'ai-generated' 
                : 'human-written'
            }`}
          >
            {sentence.sentence}{' '}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="analysis-history">
      <div className="analysis-header">
        <button onClick={onBack} className="back-button">
          Back to History
        </button>
        <h2>Analysis Details</h2>
      </div>

      <div className="analysis-content">
        <div className="analysis-text">
          <h3>Full Text Content</h3>
          {renderHighlightedText()}
          <div className="text-legend">
            <div className="legend-item">
              <span className="legend-color ai-generated"></span>
              <span>AI-generated text</span>
            </div>
            <div className="legend-item">
              <span className="legend-color human-written"></span>
              <span>Human-written text</span>
            </div>
          </div>
        </div>

        <div className="analysis-metrics">
          <div className="metric-card">
            <h3>AI Probability Score</h3>
            <Metric percentage={getAIScore()} />
            <div className="metric-details">
              <p><strong>Type:</strong> {source_type}</p>
              {filename && <p><strong>File:</strong> {filename}</p>}
              <p><strong>Date:</strong> {formatDate(timestamp)}</p>
              <p><strong>Text Length:</strong> {text_length} characters</p>
              <p><strong>Analysis Type:</strong> {analysis_type}</p>
              {analysis_type === 'sentence_level' && overall_result && (
                <>
                  <p><strong>AI Sentences:</strong> {overall_result.ai_sentence_count}</p>
                  <p><strong>Human Sentences:</strong> {overall_result.human_sentence_count}</p>
                  <p><strong>Confidence:</strong> {(overall_result.overall_confidence * 100).toFixed(1)}%</p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisHistory;