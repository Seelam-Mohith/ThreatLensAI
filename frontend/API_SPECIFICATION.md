# ThreatLens AI - Frontend API Specification

This document outlines the API contracts expected by the React frontend for the ThreatLens AI system.

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### 1. Email Phishing Detection

**Endpoint**: `POST /email-check`

**Request**:
```json
{
  "content": "string (complete email content including subject line and body)"
}
```

**Response**:
```json
{
  "prediction": "phishing|safe",
  "confidence": 0.95,
  "message": "string (detailed message about the prediction)",
  "details": [
    "string (finding 1)",
    "string (finding 2)",
    "string (finding 3)"
  ],
  "leaderboard": [
    {
      "model": "SVM (Linear, LinearSVC)",
      "f1": 0.9845,
      "accuracy": 0.9845,
      "precision": 0.9845,
      "recall": 0.9845
    }
  ]
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/email-check \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, please verify your account..."}'
```

---

### 2. URL Safety Check

**Endpoint**: `POST /url-check`

**Request**:
```json
{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "prediction": "phishing|safe",
  "confidence": 0.87,
  "message": "string (detailed message about URL safety)",
  "details": [
    "string (analysis 1)",
    "string (analysis 2)",
    "string (analysis 3)"
  ],
  "leaderboard": [
    {
      "model": "SVM (Linear, LinearSVC)",
      "f1": 0.9845,
      "accuracy": 0.9845,
      "precision": 0.9845,
      "recall": 0.9845
    }
  ]
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/url-check \
  -H "Content-Type: application/json" \
  -d '{"url": "https://suspicious-site.com"}'
```

---

### 3. Dashboard Statistics

**Endpoint**: `GET /stats`

**Response**:
```json
{
  "totalScans": 1245,
  "phishingDetected": 87,
  "legitEmailsAnalyzed": 658,
  "bestModel": "SVM (Linear, LinearSVC)",
  "lastResult": {
    "type": "email|url",
    "prediction": "phishing|safe",
    "confidence": 0.945,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Example cURL**:
```bash
curl http://localhost:5000/api/stats
```

---

### 4. Model Performance Leaderboard

**Endpoint**: `GET /models/performance`

**Response**:
```json
[
  {
    "rank": 1,
    "model": "SVM (Linear, LinearSVC)",
    "f1": 0.9845,
    "accuracy": 0.9845,
    "precision": 0.9845,
    "recall": 0.9845,
    "trainingTime": 2.74,
    "isActive": true
  },
  {
    "rank": 2,
    "model": "Random Forest (n_estimators=50)",
    "f1": 0.9821,
    "accuracy": 0.9821,
    "precision": 0.9821,
    "recall": 0.9821,
    "trainingTime": 12.27,
    "isActive": true
  }
]
```

**Example cURL**:
```bash
curl http://localhost:5000/api/models/performance
```

---

## Error Handling

All endpoints should return appropriate HTTP status codes:

**Success**: `200 OK`
```json
{
  "success": true,
  "data": { /* response data */ }
}
```

**Client Error**: `400 Bad Request`
```json
{
  "success": false,
  "error": "Invalid request parameters",
  "details": "URL field is required"
}
```

**Server Error**: `500 Internal Server Error`
```json
{
  "success": false,
  "error": "Server error occurred",
  "details": "Exception message"
}
```

---

## Response Field Descriptions

### Prediction Field
- `"phishing"` - Email/URL is identified as phishing
- `"safe"` - Email/URL is safe

### Confidence Score
- Float between `0.0` and `1.0`
- `0.0` = No confidence
- `1.0` = 100% confidence
- Display as percentage: `(confidence * 100).toFixed(1)%`

### Leaderboard Array
- Sorted by F1 score (highest first)
- Contains metrics from all trained models
- Used for model performance comparison on frontend

### Details Array
- 2-5 key findings about the email/URL
- Specific to the prediction (phishing or safe)
- Used to explain why the prediction was made

---

## Model Data Format

Each model in leaderboard should have:

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model name (e.g., "SVM (Linear, LinearSVC)") |
| `f1` | float | F1 score (0-1, display as %) |
| `accuracy` | float | Accuracy metric (0-1, display as %) |
| `precision` | float | Precision score (0-1, display as %) |
| `recall` | float | Recall/Sensitivity (0-1, display as %) |

---

## CORS Configuration

The backend should enable CORS for the frontend origin:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Frontend Expected Behavior

1. **Email Analysis Flow**:
   - User enters email content
   - Frontend sends to `/email-check`
   - Displays result with confidence and leaderboard
   - Shows risk level (phishing/safe) with visual indicators

2. **URL Analysis Flow**:
   - User enters URL
   - Frontend validates URL format
   - Sends to `/url-check`
   - Displays safety determination

3. **Dashboard Flow**:
   - Fetches `/stats` for key metrics
   - Fetches `/models/performance` for charts
   - Displays statistics and visualizations

---

## Mock Data (Frontend Fallback)

If backend is unavailable, frontend uses this mock data:

```javascript
const mockLeaderboard = [
  { 
    model: 'SVM (Linear, LinearSVC)', 
    f1: 0.9845, 
    accuracy: 0.9845, 
    precision: 0.9845, 
    recall: 0.9845 
  },
  { 
    model: 'Random Forest (n_estimators=50)', 
    f1: 0.9821, 
    accuracy: 0.9821, 
    precision: 0.9821, 
    recall: 0.9821 
  },
  { 
    model: 'Logistic Regression (L2)', 
    f1: 0.9815, 
    accuracy: 0.9815, 
    precision: 0.9816, 
    recall: 0.9815 
  },
  { 
    model: 'XGBoost Classifier', 
    f1: 0.9572, 
    accuracy: 0.9572, 
    precision: 0.9577, 
    recall: 0.9572 
  },
  { 
    model: 'Multinomial Naive Bayes', 
    f1: 0.9593, 
    accuracy: 0.9593, 
    precision: 0.9599, 
    recall: 0.9593 
  }
];
```

---

## Rate Limiting (Recommended)

- Email check: 10 requests per minute per IP
- URL check: 20 requests per minute per IP
- Stats: 100 requests per minute per IP

---

## Future Enhancements

Potential API endpoints for future development:

```
GET    /api/user/history          - Fetch user's analysis history
GET    /api/user/preferences      - Get user preferences
POST   /api/user/export-report    - Export analysis as PDF
POST   /api/feedback              - Submit feedback on predictions
GET    /api/threats/recent        - Get recent threats detected
GET    /api/models/train          - Trigger model retraining
```

---

## Development Notes

- All timestamps should be ISO 8601 format (`YYYY-MM-DDTHH:mm:ssZ`)
- All numeric percentages should be between 0 and 1 (not 0-100)
- Frontend will convert to percentage display
- Keep response size minimal for mobile performance
- Test with both small and large inputs
- Implement proper input validation on backend

---

## Contact

For questions about the API specification, refer to the frontend README.md or contact the development team.
