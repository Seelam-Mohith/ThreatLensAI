from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import os
import joblib
import numpy as np
from dotenv import load_dotenv
from google import genai
import re

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")


def build_local_explanation(email_content, prediction, confidence):
    normalized = (email_content or "").lower()
    risk_level = "high" if prediction == "phishing" else "low"

    suspicious_signals = []

    signal_checks = [
        ("urgent" in normalized or "immediately" in normalized or "asap" in normalized,
         "Uses urgency to pressure a quick response."),
        ("verify" in normalized or "confirm" in normalized or "password" in normalized or "credential" in normalized,
         "Requests verification, credentials, or sensitive account action."),
        ("click here" in normalized or "login" in normalized or "signin" in normalized,
         "Pushes the reader toward a link or login flow."),
        ("attachment" in normalized or "download" in normalized,
         "References attachments or downloads that should be treated carefully."),
        ("gift card" in normalized or "bank" in normalized or "invoice" in normalized or "payment" in normalized,
         "Touches money, billing, or other high-impact account themes."),
    ]

    for matched, description in signal_checks:
        if matched:
            suspicious_signals.append(description)

    if not suspicious_signals:
        if prediction == "phishing":
            suspicious_signals.append("The detection engine found phishing-like text patterns in the message.")
        else:
            suspicious_signals.append("The message does not show the common urgency, credential, or link patterns usually seen in phishing emails.")

    recommended_actions = (
        [
            "Do not click links, open attachments, or reply with credentials.",
            "Verify the request through a trusted channel before taking action.",
            "Report the message to your security team or mail provider if it looks suspicious.",
        ]
        if prediction == "phishing"
        else
        [
            "No obvious phishing indicators were detected in this scan.",
            "Still confirm the sender and link targets before sharing sensitive information.",
            "Keep standard caution if the email asks for payments, passwords, or attachments.",
        ]
    )

    summary = (
        f"This email was classified as {prediction} with {confidence:.0%} confidence."
        f" The current risk level is {risk_level}."
    )

    sections = [
        "Why it was classified this way:",
        *[f"- {signal}" for signal in suspicious_signals[:3]],
        "Risk level:",
        f"- {risk_level.capitalize()} risk based on the detection result and the language found in the message.",
        "What you should do:",
        *[f"- {action}" for action in recommended_actions],
    ]

    return "\n".join([summary, "", *sections])


def explain_fallback_reason(error):
    error_text = str(error)

    if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text or "quota" in error_text.lower():
        retry_match = re.search(r"retry(?: in)?\s+(\d+(?:\.\d+)?)s", error_text, flags=re.IGNORECASE)
        retry_suffix = f" Retry after about {retry_match.group(1)} seconds." if retry_match else ""
        return f"Gemini quota reached.{retry_suffix}"

    return "Gemini explanation unavailable."

def generate_ai_explanation(
    email_content,
    prediction,
    confidence
):
    if client is None:
        return {
            'text': build_local_explanation(email_content, prediction, confidence),
            'source': 'local_fallback',
            'note': 'Gemini client is not configured.',
        }
    
    prompt = f"""
    You are a cybersecurity analyst.

    Email:
    {email_content}

    Prediction:
    {prediction}

    Confidence:
    {confidence:.2%}

    Explain:
    1. Why this email was classified this way.
    2. Risk level.
    3. What the user should do.

    Keep response under 100 words.
    Use simple language.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
    except Exception as e:
        print(f"Gemini explanation failed: {e}")
        return {
            'text': build_local_explanation(email_content, prediction, confidence),
            'source': 'local_fallback',
            'note': explain_fallback_reason(e),
        }

    return {
        'text': response.text,
        'source': 'gemini',
        'note': '',
    }

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize paths
ML_EMAIL_PATH = Path(__file__).parent.parent / 'ml' / 'email'

# Load SVM model for email analysis
# Load SVM model for email analysis
svm_model = None
tfidf_vectorizer = None
model_loaded = False

LEADERBOARD_DATA = [
    {
        'model': 'SVM (Linear, LinearSVC)',
        'f1': 0.9845,
        'accuracy': 0.9845,
        'precision': 0.9845,
        'recall': 0.9845
    },
    {
        'model': 'Random Forest',
        'f1': 0.9821,
        'accuracy': 0.9821,
        'precision': 0.9821,
        'recall': 0.9821
    },
    {
        'model': 'Logistic Regression',
        'f1': 0.9815,
        'accuracy': 0.9815,
        'precision': 0.9816,
        'recall': 0.9815
    },
    {
        'model': 'XGBoost',
        'f1': 0.9572,
        'accuracy': 0.9572,
        'precision': 0.9577,
        'recall': 0.9572
    }
]

def load_email_model():
    """Load SVM model and TF-IDF vectorizer"""
    global svm_model, tfidf_vectorizer, model_loaded

    if model_loaded:
        return

    try:
        # Load SVM model
        model_path = ML_EMAIL_PATH / 'svm_model.pkl'

        if model_path.exists():
            print(f"Loading SVM model from {model_path}...")
            svm_model = joblib.load(model_path)
            print("SVM model loaded successfully")
        else:
            print(f"Warning: SVM model not found at {model_path}")

        # Load Vectorizer
        vectorizer_path = ML_EMAIL_PATH / 'vectorizer.pkl'

        if vectorizer_path.exists():
            print(f"Loading vectorizer from {vectorizer_path}...")
            tfidf_vectorizer = joblib.load(vectorizer_path)
            print("TF-IDF vectorizer loaded successfully")
        else:
            print(f"Warning: Vectorizer not found at {vectorizer_path}")

    except Exception as e:
        print(f"Error loading model files: {e}")

    model_loaded = True

# Simulated analysis function (uses ML model patterns)
def analyze_email_content(email_content):
    """
    Analyze email using SVM model or fallback to pattern matching if model unavailable
    """
    global svm_model
    
    # Lazy load model if not already loaded
    if not model_loaded:
        load_email_model()
    
    if svm_model is not None:
        try:
            # Try to use the loaded SVM model
            if hasattr(svm_model, 'predict'):
                if tfidf_vectorizer is None:
                    raise ValueError("TF-IDF vectorizer is unavailable")

                # Reshape input for sklearn
                email_vector = tfidf_vectorizer.transform([email_content])

                prediction = svm_model.predict(email_vector)[0]
                
                # Get confidence score if available
                if hasattr(svm_model, 'decision_function'):
                    confidence_score = svm_model.decision_function(email_vector)[0]

                    confidence = float(
                        1 / (1 + np.exp(-abs(confidence_score)))
                )

                confidence = round(confidence, 3)
                
                is_phishing = bool(prediction == 1 or prediction == 'phishing')
                
                details = []
                if is_phishing:
                    details = [
                        'SVM model detected phishing characteristics',
                        'Suspicious email patterns identified',
                        'Recommended: Do not click links or download attachments'
                    ]
                else:
                    details = [
                        'SVM model classified as legitimate',
                        'Email appears to be from trusted source',
                        'Standard communication patterns detected'
                    ]
                
                return {
                    'is_phishing': is_phishing,
                    'confidence': confidence,
                    'details': details,
                    'model_used': 'SVM (Linear, LinearSVC)',
                    'matches': 1 if is_phishing else 0
                }
        except Exception as e:
            print(f"Warning: SVM prediction error: {e}, falling back to pattern analysis")
            # Fallback to pattern matching
            return analyze_email_pattern(email_content)
    else:
        # Fallback to pattern matching if model not loaded
        return analyze_email_pattern(email_content)

def analyze_email_pattern(email_content):
    """
    Fallback pattern-based email analysis
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
        'model_used': 'Pattern Analysis Engine (Fallback)',
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
        
        prediction = (
            "phishing"
            if analysis["is_phishing"]
            else "safe"
        )

        explanation_result = generate_ai_explanation(
            email_content,
            prediction,
            analysis["confidence"]
        )
        
        return jsonify({
            'prediction': 'phishing' if analysis['is_phishing'] else 'safe',
            'confidence': analysis['confidence'],

            'message': (
                'This email shows characteristics of a phishing attempt. Exercise caution.'
                if analysis['is_phishing']
                else 'This email appears to be legitimate. It\'s generally safe to open.'
            ),

            'ai_explanation': explanation_result['text'],
            'explanation_source': explanation_result['source'],
            'explanation_note': explanation_result['note'],

            'details': analysis['details'],

            'leaderboard': LEADERBOARD_DATA,

            'model_used': analysis.get(
                'model_used',
                'Pattern Analysis Engine'
            )
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
