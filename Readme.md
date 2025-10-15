# Fake News Detection Project 📰

## Overview

The **Fake News Detection Project** is a full-stack, machine learning-powered application designed to analyze news content and determine its veracity. It provides **classification**, **confidence scores**, and crucial **explainability insights** to help users understand the model's decision-making process.

This system employs **Support Vector Classification (SVC)** models for both a high-level **binary** classification (True/Fake) and a more detailed **granular** classification (e.g., conspiracy, propaganda).

The application is architected as a decoupled system: a **Python backend API** is containerized with **Docker** and deployed on **Google Cloud Run**, serving predictions to a responsive **React frontend**.

---

## ✨ Features

### 🔍 Intelligent Classification
The core of the project offers two levels of prediction:
* **Binary Classification:** Categorizes the news as `"True"`, `"Fake"`, or `"Unknown / Borderline"`.
* **Granular Classification:** For articles not classified as `"True"`, a more detailed label (e.g., `"bs"`, `"conspiracy"`, `"propaganda"`) is provided, detailing the likely type of misinformation.

### 💡 Explainability and Confidence
Every prediction is accompanied by data to enhance user trust and understanding:
* **Confidence Scores:** Numerical scores (0–1) are returned for both binary and granular predictions.
* **Top Features from Input:** Highlights the key words within the *submitted text* that most influenced the prediction.
* **Top Features Overall:** Provides global top words statistically associated with the predicted granular label, offering context on the model's underlying knowledge.

### 🌐 Public API Endpoint
A fully accessible, performant public API deployed via Google Cloud Run allows easy integration and testing.

---

## 🛠️ Tech Stack

| Component | Technologies Used | Role |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript | Responsive user interface for submitting news and displaying results. |
| **Backend** | Python, Flask/FastAPI | RESTful API to handle prediction requests and serve model outputs. |
| **Machine Learning** | `scikit-learn` (SVC Models), TF-IDF | Core classification algorithms and text vectorization. |
| **Deployment** | Docker, Google Cloud Run | Containerization and serverless, scalable deployment of the API. |

---

## 💻 API Endpoint Documentation

The API is deployed on Google Cloud Run and accepts a single `POST` request with the news article text.

**Base URL:**
`https://fake-news-api-825158127731.us-central1.run.app`

### `POST /predict`

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `text` | `string` | The news article content to be analyzed. |

**Request Body Example:**

{
  "text": "Your news article text here"
}

This is the complete and highly polished README.md presented as a single file.

Markdown

# Fake News Detection Project 📰

## Overview

The **Fake News Detection Project** is a full-stack, machine learning-powered application designed to analyze news content and determine its veracity. It provides **classification**, **confidence scores**, and crucial **explainability insights** to help users understand the model's decision-making process.

This system employs **Support Vector Classification (SVC)** models for both a high-level **binary** classification (True/Fake) and a more detailed **granular** classification (e.g., conspiracy, propaganda).

The application is architected as a decoupled system: a **Python backend API** is containerized with **Docker** and deployed on **Google Cloud Run**, serving predictions to a responsive **React frontend**.

---

## ✨ Features

### 🔍 Intelligent Classification
The core of the project offers two levels of prediction:
* **Binary Classification:** Categorizes the news as `"True"`, `"Fake"`, or `"Unknown / Borderline"`.
* **Granular Classification:** For articles not classified as `"True"`, a more detailed label (e.g., `"bs"`, `"conspiracy"`, `"propaganda"`) is provided, detailing the likely type of misinformation.

### 💡 Explainability and Confidence
Every prediction is accompanied by data to enhance user trust and understanding:
* **Confidence Scores:** Numerical scores (0–1) are returned for both binary and granular predictions.
* **Top Features from Input:** Highlights the key words within the *submitted text* that most influenced the prediction.
* **Top Features Overall:** Provides global top words statistically associated with the predicted granular label, offering context on the model's underlying knowledge.

### 🌐 Public API Endpoint
A fully accessible, performant public API deployed via Google Cloud Run allows easy integration and testing.

---

## 🛠️ Tech Stack

| Component | Technologies Used | Role |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript | Responsive user interface for submitting news and displaying results. |
| **Backend** | Python, Flask/FastAPI | RESTful API to handle prediction requests and serve model outputs. |
| **Machine Learning** | `scikit-learn` (SVC Models), TF-IDF | Core classification algorithms and text vectorization. |
| **Deployment** | Docker, Google Cloud Run | Containerization and serverless, scalable deployment of the API. |

---

## 💻 API Endpoint Documentation

The API is deployed on Google Cloud Run and accepts a single `POST` request with the news article text.

**Base URL:**
`https://fake-news-api-825158127731.us-central1.run.app`

### `POST /predict`

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `text` | `string` | The news article content to be analyzed. |

**Request Body Example:**
```json
{
  "text": "Your news article text here"
}
Response Structure and Field Descriptions
Field	Type	Description
binary_prediction	string	Overall label: "Fake", "True", or "Unknown / Borderline".
binary_confidence	number	Confidence score (0–1) for the binary prediction.
C_True_confidence	number	Raw confidence score for the "True" class specifically.
granular_prediction	string	Top granular label, e.g., "bs", "conspiracy", etc.
granular_confidence_top	number	Confidence score for the top granular label.
granular_confidence_all	object	Confidence scores for all granular classes.
top_features_input	array	Top input words and their weights contributing to the prediction. [["word", weight], ...]
top_features_overall	array	Top words globally associated with the predicted granular label. [["word", weight], ...]


Response Body Example:
{
  "binary_prediction": "Fake",
  "binary_confidence": 0.93,
  "C_True_confidence": 0.07,
  "granular_prediction": "conspiracy",
  "granular_confidence_top": 0.85,
  "granular_confidence_all": {
      "bs": 0.05,
      "conspiracy": 0.85,
      "propaganda": 0.10
  },
  "top_features_input": [["word1", 0.12], ["word2", 0.08]],
 "top_features_overall": [["conspiracy_word1", 0.15], ["conspiracy_word2", 0.10]]
}

💻 Frontend Integration (React/TypeScript Example)

This snippet demonstrates a client-side function for consuming the API:

TypeScript

const handleSubmit = async (news: string) => {
  if (!news) return;
  setLoading(true);
  try {
    const response = await fetch('[https://fake-news-api-825158127731.us-central1.run.app/predict](https://fake-news-api-825158127731.us-central1.run.app/predict)', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: news }),
    });
    // Ensure the response is OK before parsing
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: PredictionResult = await response.json();
    setResult(data);
  } catch (error) {
    console.error("Error fetching prediction:", error);
  } finally {
    setLoading(false);
  }
};

Usage Notes
Submit full news text for the best prediction results.

Both binary and granular predictions provide confidence scores (0–1).

Top feature lists are crucial for understanding why a specific prediction was made.

🚀 Getting Started (Optional for Local Testing)
If you wish to test the backend API locally, follow these steps:

Clone the repository:



git clone <your-repo-url>
cd fake-news-detection
Build the Docker container:



docker build -t fake-news-api .
Run the container locally:


docker run -p 8080:8080 fake-news-api
The API will now be accessible at http://localhost:8080/predict.