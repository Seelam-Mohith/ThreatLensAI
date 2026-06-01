from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Store model leaderboard data
LEADERBOARD_DATA = [
    {'model': 'SVM (Linear, LinearSVC)', 'f1': 0.9845, 'accuracy': 0.9845, 'precision': 0.9845, 'recall': 0.9845},
    {'model': 'Random Forest (n_estimators=50)', 'f1': 0.9821, 'accuracy': 0.9821, 'precision': 0.9821, 'recall': 0.9821},
    {'model': 'Logistic Regression (L2)', 'f1': 0.9815, 'accuracy': 0.9815, 'precision': 0.9816, 'recall': 0.9815},
    {'model': 'XGBoost Classifier', 'f1': 0.9572, 'accuracy': 0.9572, 'precision': 0.9577, 'recall': 0.9572},
    {'model': 'Multinomial Naive Bayes', 'f1': 0.9593, 'accuracy': 0.9593, 'precision': 0.9599, 'recall': 0.9593},
]

# Simulated analysis function (uses ML model patterns)
def analyze_email_content(email_content):
    """
    Simulate email analysis using pattern matching.
    For production, integrate with actual trained models.
    """
    suspicious_keywords = [
        'verify account', 'confirm identity', 'urgent', 'click here',
        'update payment', 'validate credentials', 'confirm password',
        'suspicious activity', 'limited time', 'act now'
    ]
    
    email_lower = email_content.lower()
    matches = sum(1 for keyword in suspicious_keywords if keyword in email_lower)
    
    # Calculate confidence based on matches
    confidence = min(0.95, 0.5 + (matches * 0.08))
    is_phishing = matches >= 2
    
    details = []
    if any(kw in email_lower for kw in ['verify account', 'confirm identity']):
        details.append('Account verification request detected')
    if any(kw in email_lower for kw in ['urgent', 'act now', 'limited time']):
        details.append('Urgency language present')
    if any(kw in email_lower for kw in ['click here', 'update payment', 'confirm']):
        details.append('Suspicious call-to-action detected')
    if not details:
        details = ['Email appears legitimate', 'Standard communication patterns', 'No suspicious markers detected']
    
    return {
        'is_phishing': is_phishing,
        'confidence': confidence,
        'details': details,
        'matches': matches
    }

def analyze_url(url):
    """
    Simulate URL analysis using pattern matching.
    For production, integrate with actual threat intelligence.
    """
    suspicious_patterns = [
        'bit.ly', 'tinyurl', 'short.link',  # URL shorteners
        'login', 'verify', 'confirm', 'update',  # Suspicious keywords
        'secure-', 'auth-', 'admin-'  # Impersonation patterns
    ]
    
    url_lower = url.lower()
    matches = sum(1 for pattern in suspicious_patterns if pattern in url_lower)
    
    confidence = min(0.95, 0.4 + (matches * 0.15))
    is_phishing = matches >= 1
    
    details = []
    if any(p in url_lower for p in ['bit.ly', 'tinyurl', 'short']):
        details.append('URL shortener detected')
    if any(p in url_lower for p in ['login', 'verify', 'confirm']):
        details.append('Authentication pattern detected')
    if 'https' not in url:
        details.append('No HTTPS encryption')
    if not details:
        details = ['Domain appears legitimate', 'Valid HTTPS present', 'No known malicious patterns']
    
    return {
        'is_phishing': is_phishing,
        'confidence': confidence,
        'details': details,
        'matches': matches
    }

# ============ API ENDPOINTS ============

@app.route('/api/email-check', methods=['POST'])
def email_check():
    """Analyze email for phishing"""
    try:
        data = request.get_json()
        email_content = data.get('content', '')
        
        if not email_content:
            return jsonify({'error': 'Email content is required'}), 400
        
        # Analyze email
        analysis = analyze_email_content(email_content)
        
        return jsonify({
            'prediction': 'phishing' if analysis['is_phishing'] else 'safe',
            'confidence': analysis['confidence'],
            'message': (
                'This email shows characteristics of a phishing attempt. Exercise caution.'
                if analysis['is_phishing']
                else 'This email appears to be legitimate. It\'s generally safe to open.'
            ),
            'details': analysis['details'],
            'leaderboard': LEADERBOARD_DATA,
            'model_used': 'Pattern Analysis Engine'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/url-check', methods=['POST'])
def url_check():
    """Analyze URL for malicious content"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Analyze URL
        analysis = analyze_url(url)
        
        return jsonify({
            'prediction': 'phishing' if analysis['is_phishing'] else 'safe',
            'confidence': analysis['confidence'],
            'message': (
                'This URL may be malicious or designed to phish for credentials.'
                if analysis['is_phishing']
                else 'This URL appears to be safe to visit.'
            ),
            'details': analysis['details'],
            'leaderboard': LEADERBOARD_DATA,
            'model_used': 'URL Threat Analysis Engine'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        return jsonify({
            'totalScans': 1245,
            'phishingDetected': 87,
            'legitEmailsAnalyzed': 658,
            'bestModel': 'SVM (Linear, LinearSVC)',
            'lastResult': {
                'type': 'email',
                'prediction': 'safe',
                'confidence': 0.945,
                'timestamp': '2024-01-15T10:30:00Z'
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/performance', methods=['GET'])
def get_models_performance():
    """Get model performance metrics"""
    try:
        return jsonify(LEADERBOARD_DATA), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'QuantShield Backend',
        'version': '1.0.0'
    }), 200

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============ MAIN ============

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════╗
    ║   QuantShield - Backend Server         ║
    ║   Running on http://localhost:5000     ║
    ║   API Base: http://localhost:5000/api  ║
    ╚════════════════════════════════════════╝
    
    Available Endpoints:
    - POST   /api/email-check          (Analyze emails)
    - POST   /api/url-check            (Analyze URLs)
    - GET    /api/stats                (Dashboard stats)
    - GET    /api/models/performance   (Model leaderboard)
    - GET    /api/health               (Health check)
    
    Frontend: http://localhost:3000
    """)
    
    app.run(
        host='localhost',
        port=5000,
        debug=True,
        use_reloader=True
    )
