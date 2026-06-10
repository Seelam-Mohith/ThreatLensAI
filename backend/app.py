from email.mime import message
from unittest import result
from unittest import result

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import os
import joblib
import numpy as np
import logging
from dotenv import load_dotenv
from google import genai
import re
from network_ids import analyze_network_capture, load_network_artifacts

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


def build_local_sms_explanation(message_content, prediction, confidence):
    normalized = (message_content or "").lower()
    risk_level = "high" if prediction == "spam" else "low"

    suspicious_signals = []
    signal_checks = [
        (
            any(keyword in normalized for keyword in ["urgent", "immediately", "act now", "limited time"]),
            "Uses urgency to pressure a quick response."
        ),
        (
            any(keyword in normalized for keyword in ["verify", "confirm", "password", "otp", "bank details", "account"]),
            "Requests verification, account details, or other sensitive information."
        ),
        (
            any(keyword in normalized for keyword in ["http://", "https://", "bit.ly", "tinyurl", "link"]),
            "Pushes the reader toward a link or external action."
        ),
        (
            any(keyword in normalized for keyword in ["refund", "income tax", "work from home", "whatsapp", "earn ₹", "earn rs"]),
            "Touches common scam themes like refunds, fake jobs, or money offers."
        ),
    ]

    for matched, description in signal_checks:
        if matched:
            suspicious_signals.append(description)

    if not suspicious_signals:
        if prediction == "spam":
            suspicious_signals.append("The detection engine found scam-like wording patterns in the SMS.")
        else:
            suspicious_signals.append("The message does not show the common urgency, credential, or malicious-link patterns usually seen in scam SMS messages.")

    recommended_actions = (
        [
            "Do not click links, reply with personal information, or contact the sender on untrusted numbers.",
            "Verify the claim using an official website or phone number before taking action.",
            "Report and delete the SMS if it appears fraudulent."
        ]
        if prediction == "spam"
        else
        [
            "No strong scam indicators were detected in this scan.",
            "Still avoid sharing OTPs, passwords, or banking information by SMS.",
            "Confirm unexpected payment or account requests through an official channel."
        ]
    )

    summary = (
        f"This SMS was classified as {prediction} with {confidence:.0%} confidence."
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


def build_local_url_explanation(url, prediction, confidence):
    normalized = (url or "").lower()
    risk_level = "high" if prediction == "phishing" else "low"

    suspicious_signals = []
    signal_checks = [
        (
            any(keyword in normalized for keyword in ["bit.ly", "tinyurl", "short.link"]),
            "Uses a shortened link pattern that can hide the real destination.",
        ),
        (
            any(keyword in normalized for keyword in ["login", "verify", "confirm", "update"]),
            "Contains credential or account-action language often used in phishing URLs.",
        ),
        (
            any(keyword in normalized for keyword in ["secure-", "auth-", "admin-"]),
            "Includes impersonation-style subdomain or hostname wording.",
        ),
        (
            not normalized.startswith("https://"),
            "Does not start with HTTPS, so transport security is weaker or unclear.",
        ),
    ]

    for matched, description in signal_checks:
        if matched:
            suspicious_signals.append(description)

    if not suspicious_signals:
        if prediction == "phishing":
            suspicious_signals.append("The URL model found phishing-like patterns in the link structure.")
        else:
            suspicious_signals.append("The URL does not show the common shortening, credential, or impersonation patterns usually seen in phishing links.")

    recommended_actions = (
        [
            "Avoid opening the link or entering credentials into any page it leads to.",
            "Verify the destination through an official website or trusted bookmark first.",
            "Share the link with your security team if it was unexpected or urgent.",
        ]
        if prediction == "phishing"
        else
        [
            "No strong phishing indicators were detected in this scan.",
            "Still confirm the domain carefully before signing in or sharing sensitive information.",
            "Keep normal caution with shortened links or unexpected account-related URLs.",
        ]
    )

    summary = (
        f"This URL was classified as {prediction} with {confidence:.0%} confidence."
        f" The current risk level is {risk_level}."
    )

    sections = [
        "Why it was classified this way:",
        *[f"- {signal}" for signal in suspicious_signals[:3]],
        "Risk level:",
        f"- {risk_level.capitalize()} risk based on the model result and the URL wording.",
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


def generate_ai_sms_explanation(
    message_content,
    prediction,
    confidence
):
    if client is None:
        return {
            'text': build_local_sms_explanation(message_content, prediction, confidence),
            'source': 'local_fallback',
            'note': 'Gemini client is not configured.',
        }

    prompt = f"""
    You are a cybersecurity analyst.

    SMS:
    {message_content}

    Prediction:
    {prediction}

    Confidence:
    {confidence:.2%}

    Explain:
    1. Why this SMS was classified this way.
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
        print(f"Gemini SMS explanation failed: {e}")
        return {
            'text': build_local_sms_explanation(message_content, prediction, confidence),
            'source': 'local_fallback',
            'note': explain_fallback_reason(e),
        }

    return {
        'text': response.text,
        'source': 'gemini',
        'note': '',
    }


def generate_ai_url_explanation(
    url,
    prediction,
    confidence
):
    if client is None:
        return {
            'text': build_local_url_explanation(url, prediction, confidence),
            'source': 'local_fallback',
            'note': 'Gemini client is not configured.',
        }

    prompt = f"""
    You are a cybersecurity analyst.

    URL:
    {url}

    Prediction:
    {prediction}

    Confidence:
    {confidence:.2%}

    Explain:
    1. Why this URL was classified this way.
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
        print(f"Gemini URL explanation failed: {e}")
        return {
            'text': build_local_url_explanation(url, prediction, confidence),
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
logging.basicConfig(level=logging.INFO)

# Initialize paths
ML_EMAIL_PATH = Path(__file__).parent.parent / 'ml' / 'email'
ML_NETWORK_PATH = Path(__file__).parent.parent / 'ml' / 'network'

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
    
ML_SMS_PATH = Path(__file__).parent.parent / 'ml' / 'sms'
ML_URL_PATH = Path(__file__).parent.parent / 'ml' / 'url'

sms_model = None
sms_vectorizer = None
sms_label_encoder = None
sms_model_loaded = False
url_model = None
url_model_loaded = False
network_model = None
network_scaler = None
network_model_loaded = False

def load_sms_model():

    global sms_model
    global sms_vectorizer
    global sms_label_encoder
    global sms_model_loaded

    if sms_model_loaded:
        return

    try:

        sms_model = joblib.load(
            ML_SMS_PATH / "svm_model_SMS.pkl"
        )

        sms_vectorizer = joblib.load(
            ML_SMS_PATH / "vectorizer_SMS.pkl"
        )

        sms_label_encoder = joblib.load(
            ML_SMS_PATH / "label_encoder_SMS.pkl"
        )

        print("SMS model loaded successfully")
        print("Classes:", sms_label_encoder.classes_)

    except Exception as e:
        print(f"SMS model load error: {e}")

    sms_model_loaded = True
    
def analyze_sms_content(message):

    global sms_model

    if not sms_model_loaded:
        load_sms_model()

    try:

        vector = sms_vectorizer.transform([message])

        prediction = sms_model.predict(vector)

        print("Raw prediction:", prediction)

        result = sms_label_encoder.inverse_transform(
        prediction
        )[0]

        print("Decoded prediction:", result)

        if isinstance(result, (int, np.integer)):
            class_id = int(result)
            normalized_result = "ham" if class_id == 0 else "spam"
        else:
            normalized_result = str(result).strip().lower()
            class_id = None
            if normalized_result.isdigit():
                class_id = int(normalized_result)
                normalized_result = "ham" if class_id == 0 else "spam"

        is_spam = normalized_result in {"spam", "smishing", "scam"}

        print("Is spam:", is_spam)

        scores = sms_model.decision_function(vector)

        print("Scores:", scores)

        exp_scores = np.exp(scores)

        probs = exp_scores / np.sum(exp_scores)

        confidence = round(
            float(np.max(probs)),
            3
        )

        print("Confidence:", confidence)

        message_lower = message.lower()
        details = []

        suspicious_rules = [
            (
                any(keyword in message_lower for keyword in ["work from home", "earn rs", "earn ₹", "earn money", "/week"]),
                "Income bait or unrealistic earning claim detected.",
            ),
            (
                any(keyword in message_lower for keyword in ["whatsapp", "apply now", "resume online", "selected candidate"]),
                "Recruitment-style call to action matches common scam outreach.",
            ),
            (
                any(keyword in message_lower for keyword in ["refund", "income tax", "tax department", "submit bank details"]),
                "Government or refund impersonation language is present.",
            ),
            (
                any(keyword in message_lower for keyword in ["bank details", "account", "password", "otp", "verify", "confirm"]),
                "Sensitive account or verification language is present.",
            ),
            (
                any(keyword in message_lower for keyword in ["click", "link", "bit.ly", "tinyurl", "http://", "https://"]),
                "The message contains a link or link-like call to action.",
            ),
            (
                any(keyword in message_lower for keyword in ["urgent", "immediately", "act now", "limited time"]),
                "Urgency language detected in the SMS.",
            ),
        ]

        rule_hits = 0
        for matched, description in suspicious_rules:
            if matched:
                rule_hits += 1
                details.append(description)

        if not is_spam and rule_hits >= 2:
            is_spam = True
            normalized_result = "spam"
            confidence = max(confidence, min(0.95, 0.55 + (rule_hits * 0.1)))
            details.insert(0, "Rule-based safety override triggered because multiple scam indicators were found.")

        if not details:
            details = (
                [
                    "The SMS matches spam-like wording patterns learned by the model.",
                    "Treat links, reply requests, and personal data prompts with caution.",
                ]
                if is_spam
                else [
                    "No strong scam indicators were surfaced in this SMS.",
                    "The wording looks closer to normal conversational or transactional text.",
                ]
            )

        return {
            "is_spam": is_spam,
            "prediction": normalized_result,
            "confidence": confidence,
            "details": details[:3],
            "model_used": "SVM SMS Classifier",
        }

    except Exception as e:

        print(f"SMS Prediction Error: {e}")

        return {
            "is_spam": False,
            "prediction": "unknown",
            "confidence": 0,
            "details": [
                "The SMS model could not complete analysis.",
                "A fallback result was returned without detailed findings.",
            ],
            "model_used": "SVM SMS Classifier",
        }

def load_url_model():
    global url_model
    global url_model_loaded

    if url_model_loaded:
        return

    try:
        model_path = ML_URL_PATH / "model.pkl"

        if model_path.exists():
            print(f"Loading URL model from {model_path}...")
            url_model = joblib.load(model_path)
            print("URL model loaded successfully")
        else:
            print(f"Warning: URL model not found at {model_path}")
    except Exception as e:
        print(f"URL model load error: {e}")

    url_model_loaded = True

def load_network_model():
    global network_model
    global network_scaler
    global network_model_loaded

    if network_model_loaded:
        return

    try:
        model_path = ML_NETWORK_PATH / "portscan_ids.pkl"
        scaler_path = ML_NETWORK_PATH / "scaler.pkl"

        if not model_path.exists():
            print(f"Warning: Network model not found at {model_path}")
        elif not scaler_path.exists():
            print(f"Warning: Network scaler not found at {scaler_path}")
        else:
            network_model, network_scaler = load_network_artifacts(model_path, scaler_path)
            print("Network IDS model and scaler loaded successfully")
    except Exception as e:
        print(f"Network IDS model load error: {e}")

    network_model_loaded = True

def analyze_url(url):
    """
    Analyze a URL using the trained URL model with a pattern fallback.
    """
    global url_model

    if not url_model_loaded:
        load_url_model()

    if url_model is not None:
        try:
            prediction = int(url_model.predict([url])[0])
            probabilities = url_model.predict_proba([url])[0]
            confidence = round(float(max(probabilities)), 3)
            is_phishing = prediction == 1

            details = (
                [
                    "The trained URL model found phishing-like characteristics.",
                    "Treat this link carefully before opening it.",
                ]
                if is_phishing
                else [
                    "The trained URL model classified this link as legitimate.",
                    "No strong phishing signal was surfaced by the model.",
                ]
            )

            return {
                'is_phishing': is_phishing,
                'confidence': confidence,
                'details': details,
                'matches': 1 if is_phishing else 0,
                'model_used': 'URL Classifier Model'
            }
        except Exception as e:
            print(f"URL prediction error: {e}, falling back to pattern analysis")

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
        'matches': matches,
        'model_used': 'Pattern Analysis Engine (Fallback)'
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
    
@app.route('/api/sms-check', methods=['POST'])
def sms_check():

    try:

        data = request.get_json()

        print("SMS Request:", data)

        message = data.get('content', '')

        print("Message:", message)

        if not message:
            return jsonify({
                'error': 'SMS content required'
            }), 400

        analysis = analyze_sms_content(message)
        prediction = 'spam' if analysis['is_spam'] else 'ham'
        explanation_result = generate_ai_sms_explanation(
            message,
            prediction,
            analysis['confidence']
        )

        return jsonify({

            'prediction': prediction,

            'confidence':
                analysis['confidence'],

            'message':
                'Spam SMS detected'
                if analysis['is_spam']
                else 'Legitimate SMS',

            'ai_explanation': explanation_result['text'],
            'explanation_source': explanation_result['source'],
            'explanation_note': explanation_result['note'],

            'details': analysis.get('details', []),

            'leaderboard': LEADERBOARD_DATA,

            'model_used':
                analysis.get('model_used', 'SVM SMS Classifier')
        })

    except Exception as e:

        return jsonify({
            'error': str(e)
        }), 500

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
        prediction = 'phishing' if analysis['is_phishing'] else 'safe'
        explanation_result = generate_ai_url_explanation(
            url,
            prediction,
            analysis['confidence']
        )
        
        return jsonify({
            'prediction': prediction,
            'confidence': analysis['confidence'],
            'message': (
                'This URL may be malicious or designed to phish for credentials.'
                if analysis['is_phishing']
                else 'This URL appears to be safe to visit.'
            ),
            'ai_explanation': explanation_result['text'],
            'explanation_source': explanation_result['source'],
            'explanation_note': explanation_result['note'],
            'details': analysis['details'],
            'leaderboard': LEADERBOARD_DATA,
            'model_used': analysis.get('model_used', 'URL Threat Analysis Engine')
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-check', methods=['POST'])
def network_check():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'PCAP or PCAPNG file is required under the "file" field.'}), 400

        upload = request.files['file']
        if not upload or not upload.filename:
            return jsonify({'error': 'A valid .pcap or .pcapng file is required.'}), 400

        suffix = Path(upload.filename).suffix.lower()
        if suffix not in {'.pcap', '.pcapng'}:
            return jsonify({'error': 'Only .pcap and .pcapng files are supported.'}), 400

        if not network_model_loaded:
            load_network_model()

        if network_model is None or network_scaler is None:
            return jsonify({'error': 'Network IDS model artifacts are unavailable.'}), 500

        analysis = analyze_network_capture(upload, network_model, network_scaler)
        summary = analysis['summary']

        return jsonify({
            'prediction': summary['prediction'],
            'confidence': summary['confidence'],
            'message': summary['message'],
            'model_used': 'Random Forest Portscan IDS',
            'filename': analysis['filename'],
            'flows_analyzed': analysis['flows_analyzed'],
            'feature_columns': analysis['feature_columns'],
            'feature_logs': analysis['feature_logs'],
            'flow_results': analysis['flow_results'],
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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
    - POST   /api/network-check        (Analyze PCAP/PCAPNG captures)
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
