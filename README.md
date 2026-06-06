# ThreatLens-AI
**An intelligent threat detection system for identifying phishing emails and malicious URLs.**

ThreatLensAI is an intelligent cybersecurity platform designed to detect phishing emails and malicious URLs using machine learning. The system combines trained classification models with a modern web interface to provide real-time threat analysis, risk assessment, and detailed detection reports.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)](https://flask.palletsprojects.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Latest-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## Overview

Cyber threats such as phishing campaigns and malicious websites continue to be among the most common attack vectors. ThreatLensAI helps users identify and analyze suspicious emails and URLs by leveraging machine learning models trained on labeled security datasets.

The platform provides fast and reliable threat detection through an interactive web application, enabling users to assess potential risks before interacting with suspicious content.

## Features

* Phishing email detection using machine learning
* Malicious URL classification and risk assessment
* Real-time threat analysis
* Confidence-based prediction scores
* Interactive dashboard for analysis and monitoring
* RESTful API for model inference
* Performance tracking and evaluation tools

## System Architecture

```text
Frontend (React + Vite)
          │
          ▼
Backend (Flask API)
          │
          ▼
Machine Learning Layer
├── Email Phishing Detection
└── URL Threat Detection
```

## Technology Stack

### Frontend

* React
* Vite
* Tailwind CSS

### Backend

* Python
* Flask

### Machine Learning

* XGBoost
* Scikit-learn
* Pandas
* NumPy

## Project Structure

```text
ThreatLensAI/
│
├── backend/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── ml/
│   ├── email/
│   └── url/
│
├── train_with_xgboost.py
├── evaluate_on_new_dataset.py
└── README.md
```

## Installation

### Clone Repository

```bash
git clone https://github.com/Seelam-Mohith/ThreatLensAI.git
cd ThreatLensAI
```

### Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend

```bash
cd backend
python app.py
```

### Start Frontend

```bash
cd frontend
npm run dev
```

The application will be available locally through the Vite development server.

## Machine Learning Models

### Email Phishing Detection

* Model: XGBoost Classifier
* Purpose: Identify phishing and fraudulent emails
* Output: Threat classification with confidence score

### URL Threat Detection

* Model: XGBoost Classifier
* Purpose: Detect malicious and suspicious URLs
* Output: Risk prediction with confidence score

## Future Enhancements

* Real-time email integration
* Browser extension for URL scanning
* Threat intelligence integration
* Explainable AI (XAI) for model predictions
* User authentication and history tracking
* Cloud deployment and scalability improvements

## Author

**Seelam Mohith**

GitHub: https://github.com/Seelam-Mohith
