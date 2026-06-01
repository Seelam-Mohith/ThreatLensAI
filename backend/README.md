# QuantShield Backend

Flask backend API for the QuantShield phishing detection system.

## Installation

### Requirements
- Python 3.8+
- pip or conda

### Setup

1. Install dependencies in your `.venv`:
```bash
# From the root QuantShield directory
pip install flask flask-cors
```

2. Run the backend server:
```bash
python backend/app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Email Analysis
```
POST /api/email-check
Content-Type: application/json

{
  "content": "email text here"
}
```

**Response:**
```json
{
  "prediction": "phishing|safe",
  "confidence": 0.95,
  "message": "...",
  "details": ["...", "..."],
  "leaderboard": [...],
  "model_used": "Pattern Analysis Engine"
}
```

### URL Analysis
```
POST /api/url-check
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "prediction": "phishing|safe",
  "confidence": 0.87,
  "message": "...",
  "details": ["...", "..."],
  "leaderboard": [...],
  "model_used": "URL Threat Analysis Engine"
}
```

### Dashboard Statistics
```
GET /api/stats
```

### Model Performance
```
GET /api/models/performance
```

### Health Check
```
GET /api/health
```

## Architecture

```
backend/
├── app.py                 (Flask application with routes)
├── requirements.txt       (Python dependencies)
├── package.json          (Node dependencies reference)
└── README.md             (This file)
```

## Features

- ✅ CORS enabled for frontend integration
- ✅ Pattern-based email analysis
- ✅ URL threat detection
- ✅ Model leaderboard endpoint
- ✅ Health check endpoint
- ✅ Comprehensive error handling
- ✅ JSON API responses

## Future Enhancements

- Integrate actual ML models from `ml/email/email_model.py`
- Add user authentication
- Implement request rate limiting
- Add analysis history storage
- Create database for model predictions
- Add webhook support for automated scanning
- Implement threat intelligence feeds

## Running Both Frontend and Backend

In separate terminals:

**Terminal 1 - Backend:**
```bash
cd "c:\Users\seela\OneDrive\Documents\All_Coding\ThreatLens AI"
python backend/app.py
```

**Terminal 2 - Frontend:**
```bash
cd "c:\Users\seela\OneDrive\Documents\All_Coding\ThreatLens AI\frontend"
npm run dev
```

Then visit: `http://localhost:3000`

## Debugging

- Backend logs appear in terminal where you ran `python backend/app.py`
- Frontend errors appear in browser console
- Use `curl` or Postman to test API endpoints directly

## Production Considerations

- Replace pattern-based analysis with actual ML models
- Add request validation and sanitization
- Implement rate limiting
- Set up logging and monitoring
- Use environment variables for configuration
- Add database for caching and history
- Deploy with production WSGI server (gunicorn, etc.)
