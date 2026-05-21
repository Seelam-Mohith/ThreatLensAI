# ThreatLens AI 🛡️

**An intelligent threat detection system for identifying phishing emails and malicious URLs using machine learning.**

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)](https://flask.palletsprojects.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Latest-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Setup & Running](#setup--running)
- [API Endpoints](#api-endpoints)
- [Model Details](#model-details)
- [Contributing](#contributing)

## 🎯 Overview

ThreatLens AI is a comprehensive threat detection platform that leverages machine learning to identify and analyze phishing emails and malicious URLs. The system combines advanced ML models with an intuitive web interface to provide real-time threat analysis and reporting.

### Key Capabilities

- **Email Phishing Detection**: Analyze email content and metadata to identify phishing attempts
- **URL Malicious Detection**: Detect malicious or suspicious URLs with high accuracy
- **Real-time Analysis**: Instant threat assessment with detailed reports
- **Interactive Dashboard**: User-friendly interface for threat analysis and monitoring
- **Model Performance Tracking**: Monitor model accuracy and performance metrics

## ✨ Features

### 🔍 Detection Models
- **Email Phishing Model**: XGBoost-based classifier for email threat detection
- **URL Malware Model**: Machine learning classifier for URL threat detection
- High accuracy detection with detailed confidence scores

### 📊 Analytics & Reporting
- Real-time threat assessment
- Detailed analysis reports
- Performance leaderboard
- Visual threat indicators

### 🎨 User Interface
- Modern, responsive web application
- Clean dashboard for threat analysis
- Email and URL analyzer tools
- Comprehensive leaderboard with metrics

### ⚙️ Backend Services
- RESTful API for threat analysis
- Model inference pipeline
- Data processing and validation
- Request/response logging

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Vite)   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Backend       │
│   (Flask API)   │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  ML Pipeline         │
├──────────────────────┤
│ • Email Model        │
│ • URL Model          │
│ • Data Processing    │
└──────────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 18**: UI library for interactive components
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **PostCSS**: CSS transformation

### Backend
- **Python 3.10+**: Core language
- **Flask**: Lightweight web framework
- **XGBoost**: Gradient boosting for ML models
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning utilities

### ML & Data
- **Machine Learning**: XGBoost classifiers
- **Data Processing**: Pandas, NumPy
- **Model Evaluation**: Scikit-learn metrics

## 📁 Project Structure

```
ThreatLens AI/
├── backend/                    # Flask backend service
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── package.json           # Node dependencies (if applicable)
│   └── README.md              # Backend documentation
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   │   ├── LeaderboardTable.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── ResultCard.jsx
│   │   ├── pages/            # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── EmailAnalyzer.jsx
│   │   │   ├── Home.jsx
│   │   │   └── URLAnalyzer.jsx
│   │   ├── hooks/            # Custom React hooks
│   │   │   └── useAnalysis.js
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── App.jsx           # Root component
│   │   └── main.jsx          # Entry point
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS config
│   ├── postcss.config.js     # PostCSS configuration
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   └── README.md             # Frontend documentation
│
├── ml/                        # Machine learning models
│   ├── email/
│   │   ├── email_model.py    # Email phishing model
│   │   └── phishing_email.csv # Training dataset (ignored)
│   └── url/
│       ├── url_model.py      # URL malware model
│       ├── malicious_phish.csv # Training dataset (ignored)
│       └── README.md         # ML documentation
│
├── evaluate_on_new_dataset.py # Model evaluation script
├── train_with_xgboost.py     # Model training script
└── README.md                  # This file
```

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- pip (Python package manager)
- npm or yarn (Node package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/Seelam-Mohith/ThreatLensAI.git
cd ThreatLensAI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install
```

## 🚀 Setup & Running

### Running the Backend

```bash
cd backend

# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start Flask server
python app.py

# Server runs on http://localhost:5000 (or specified port)
```

### Running the Frontend

```bash
cd frontend

# Development server with hot reload
npm run dev
# or
yarn dev

# Application opens at http://localhost:5173 (or specified port)

# Build for production
npm run build
# or
yarn build
```

### Running Both Simultaneously

From the project root:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🔌 API Endpoints

See [API_SPECIFICATION.md](frontend/API_SPECIFICATION.md) for detailed API documentation.

### Core Endpoints

- **Email Analysis**
  - `POST /api/analyze/email` - Analyze email for phishing threats
  
- **URL Analysis**
  - `POST /api/analyze/url` - Analyze URL for malicious content

- **Results**
  - `GET /api/results` - Fetch analysis results
  - `GET /api/results/{id}` - Get specific analysis result

## 🤖 Model Details

### Email Phishing Detection
- **Model Type**: XGBoost Classifier
- **Training Data**: Labeled email dataset
- **Features**: Email content, sender information, links, attachments
- **Output**: Phishing probability score (0-1)

### URL Malware Detection
- **Model Type**: XGBoost Classifier
- **Training Data**: Labeled URL dataset (43.55 MB)
- **Features**: URL characteristics, domain info, path analysis
- **Output**: Maliciousness probability score (0-1)

### Training & Evaluation

```bash
# Train models with XGBoost
python train_with_xgboost.py

# Evaluate on new dataset
python evaluate_on_new_dataset.py
```

## 📈 Performance

The models are trained and evaluated on comprehensive datasets to ensure high accuracy and reliability in threat detection.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Seelam Mohith**
- GitHub: [@Seelam-Mohith](https://github.com/Seelam-Mohith)

## 📧 Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/Seelam-Mohith/ThreatLensAI/issues).

## 🙏 Acknowledgments

- XGBoost for powerful machine learning models
- React and Vite for modern web development
- Flask for reliable backend service
- All contributors and supporters

---

<div align="center">

**[⬆ back to top](#threatLens-ai-)**

</div>
