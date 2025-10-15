import { useState } from 'react';
import './App.css';

interface PredictionResult {
  // Binary Classification Results
  binary_prediction: string; // e.g., "Fake", "Unknown / Borderline", "True"
  binary_confidence: number; // The confidence in the predicted binary label (Fake or True)
  C_True_confidence: number; // The raw confidence score for the TRUE class (C_True)

  // Granular Classification Results (only present if binary_prediction != "True")
  granular_prediction: string | 'N/A'; // The top granular label (e.g., "bs", "conspiracy")
  granular_confidence_top: number | 'N/A'; // The confidence score for the granular_prediction
  granular_confidence_all: Record<string, number> | 'N/A'; // Breakdown of confidence for ALL granular classes

  // Explainability & Insights
  top_features_input: [string, number][] | 'N/A'; // Top words from the INPUT that pushed the prediction
  top_features_overall: [string, number][] | 'N/A'; // Top words associated with the predicted granular label globally
}

function App() {
  const [news, setNews] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!news) return;
    setLoading(true);

    try {
      
      const response = await fetch('https://fake-news-api-825158127731.us-central1.run.app/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: news }),
      });

      const data: PredictionResult = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to render a list of features
  const renderFeatures = (features: [string, number][] | 'N/A') => {
    if (features === 'N/A') {
      return <li>N/A</li>;
    }
    if (features.length === 0) {
      return <li>No significant features found in the top 200 coefficients.</li>;
    }
    return features.map(([feature, weight]) => (
      <li key={feature}>
        {feature}: <strong>{weight.toFixed(4)}</strong>
      </li>
    ));
  };

  return (
    <div className="app-container">
      <div className="news-card">
        <label className="news-label">Fake news:</label>
        <input
          type="text"
          placeholder="Provide news here..."
          value={news}
          onChange={(e) => setNews(e.target.value)}
          className="news-input"
        />
        <button onClick={handleSubmit} disabled={loading} className="submit-btn">
          {loading ? "Checking..." : "Check"}
        </button>
      </div>

      {result && (
        <div className="result-card">
          <h2>✅ Prediction Results</h2>
          
          {/* Binary Results */}
          <div className="section">
            <h3>Binary Classification</h3>
            <p><strong>Final Label:</strong> {result.binary_prediction}</p>
            <p><strong>Conf. in Predicted Label:</strong> {result.binary_confidence.toFixed(2)}%</p>
            <p><strong>Raw C_True Conf. (Threshold Base):</strong> {result.C_True_confidence.toFixed(2)}%</p>
          </div>

          {/* Granular Results - Only show if not high-confidence True */}
          {result.granular_prediction !== 'N/A' && (
            <div className="section">
              <h3>Granular Analysis</h3>
              <p><strong>Predicted Sub-Type:</strong> 
                <span className="granular-label">{result.granular_prediction}</span> 
                (Conf: {typeof result.granular_confidence_top === 'number' ? result.granular_confidence_top.toFixed(2) : result.granular_confidence_top}%)
              </p>
              
              {/* Full Confidence Breakdown */}
              {result.granular_confidence_all !== 'N/A' && (
                <>
                  <p><strong>Full Confidence Breakdown:</strong></p>
                  <ul className="confidence-list">
                    {Object.entries(result.granular_confidence_all).map(([cls, conf]) => (
                      <li key={cls}>{cls}: {conf.toFixed(2)}%</li>
                    ))}
                  </ul>
                </>
              )}

              {/* Explainability & Insights */}
              <div className="explainability-section">
                <h3>🔍 Explainability & Insights</h3>
                
                {/* Top Input Features */}
                <p><strong>Top Features in Input Text (What drove the prediction):</strong></p>
                <ul className="feature-list">
                  {renderFeatures(result.top_features_input)}
                </ul>

                {/* Top Global Features */}
                <p><strong>Top Global Features for '{result.granular_prediction}' (Context):</strong></p>
                <ul className="feature-list">
                  {renderFeatures(result.top_features_overall)}
                </ul>
              </div>
            </div>
          )}
          
          {result.granular_prediction === 'N/A' && (
             <p className="high-conf-note">No granular analysis performed because Binary Prediction was <strong>True</strong> with high confidence (&gt;=60%).</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;