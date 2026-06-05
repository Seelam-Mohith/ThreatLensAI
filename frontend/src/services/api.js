import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Mock data for demonstration
const mockLeaderboard = [
  { model: 'SVM (Linear, LinearSVC)', f1: 0.9845, accuracy: 0.9845, precision: 0.9845, recall: 0.9845 },
  { model: 'Random Forest (n_estimators=50)', f1: 0.9821, accuracy: 0.9821, precision: 0.9821, recall: 0.9821 },
  { model: 'Logistic Regression (L2)', f1: 0.9815, accuracy: 0.9815, precision: 0.9816, recall: 0.9815 },
  { model: 'XGBoost Classifier', f1: 0.9572, accuracy: 0.9572, precision: 0.9577, recall: 0.9572 },
  { model: 'Multinomial Naive Bayes', f1: 0.9593, accuracy: 0.9593, precision: 0.9599, recall: 0.9593 },
]

export const emailApi = {
  async checkEmail(emailContent) {
    try {
      // Try to call the backend API
      const response = await apiClient.post('/email-check', { content: emailContent })
      return {
        isPhishing: response.data.prediction === 'phishing',
        confidence: response.data.confidence,
        message: response.data.message,
        explanation: response.data.ai_explanation || '',
        explanationSource: response.data.explanation_source || 'unknown',
        explanationNote: response.data.explanation_note || '',
        details: response.data.details || [],
        leaderboard: response.data.leaderboard || mockLeaderboard,
        modelUsed: response.data.model_used || '',
      }
    } catch (error) {
      console.warn('API call failed, using mock data:', error.message)
      // Fallback to mock data for demo
      const isPhishing = Math.random() > 0.7
      return {
        isPhishing,
        confidence: 0.85 + Math.random() * 0.15,
        message: isPhishing
          ? 'This email shows characteristics of a phishing attempt. Exercise caution.'
          : 'This email appears to be legitimate. It\'s generally safe to open.',
        explanation: isPhishing
          ? 'This message uses common phishing patterns like urgency and credential requests.'
          : 'This message looks routine and does not show obvious phishing indicators.',
        explanationSource: 'demo',
        explanationNote: 'Backend API unavailable.',
        details: [
          isPhishing ? 'Suspicious sender domain' : 'Verified sender',
          isPhishing ? 'Unknown links detected' : 'No suspicious links',
          isPhishing ? 'Urgency language present' : 'Standard communication',
        ],
        leaderboard: mockLeaderboard,
        modelUsed: 'Demo Analysis Engine',
      }
    }
  },
}

export const urlApi = {
  async checkUrl(url) {
    try {
      // Try to call the backend API
      const response = await apiClient.post('/url-check', { url })
      return {
        isPhishing: response.data.prediction === 'phishing',
        confidence: response.data.confidence,
        message: response.data.message,
        details: response.data.details || [],
        leaderboard: response.data.leaderboard || mockLeaderboard,
      }
    } catch (error) {
      console.warn('API call failed, using mock data:', error.message)
      // Fallback to mock data for demo
      const isPhishing = Math.random() > 0.8
      return {
        isPhishing,
        confidence: 0.82 + Math.random() * 0.18,
        message: isPhishing
          ? 'This URL may be malicious or designed to phish for credentials.'
          : 'This URL appears to be safe to visit.',
        details: [
          isPhishing ? 'Domain age suspicious' : 'Verified domain',
          isPhishing ? 'SSL certificate issues' : 'Valid SSL certificate',
          isPhishing ? 'Known phishing pattern' : 'No known threats',
        ],
        leaderboard: mockLeaderboard,
      }
    }
  },
}

export const smsApi = {
  async checkSms(smsContent) {
    try {

      const response = await apiClient.post(
        '/sms-check',
        {
          content: smsContent
        }
      )

      return {
        isPhishing: response.data.prediction === 'spam',
        confidence: response.data.confidence || 0,
        message: response.data.message || '',
        explanation: response.data.ai_explanation || '',
        explanationSource: response.data.explanation_source || 'unknown',
        explanationNote: response.data.explanation_note || '',
        details: response.data.details || [],
        leaderboard: response.data.leaderboard || mockLeaderboard,
        modelUsed: response.data.model_used || 'SVM SMS Classifier',
      }

    } catch (error) {

      console.warn(
        'API call failed, using mock data for SMS:',
        error.message
      )

      const isPhishing = Math.random() > 0.75

      return {
        isPhishing,
        confidence: 0.8 + Math.random() * 0.18,

        message: isPhishing
          ? 'This SMS looks suspicious and may be part of a phishing/scam.'
          : 'This SMS appears legitimate.',

        explanation: isPhishing
          ? 'This SMS uses scam-style patterns such as money bait, urgent action, or requests to continue on another channel.'
          : 'This SMS looks routine and does not show strong scam indicators in the fallback demo analysis.',
        explanationSource: 'demo',
        explanationNote: 'Backend API unavailable.',

        details: [
          isPhishing
            ? 'Spam keywords detected'
            : 'No suspicious indicators found',

          isPhishing
            ? 'Potential phishing content'
            : 'Message appears normal',
        ],

        leaderboard: mockLeaderboard,
        modelUsed: 'Fallback Demo Engine',
      }
    }
  },
}


export const dashboardApi = {
  async getStats() {
    try {
      const response = await apiClient.get('/stats')
      return response.data
    } catch (error) {
      console.warn('API call failed, using mock stats:', error.message)
      return {
        totalScans: 1245,
        phishingDetected: 87,
        legitEmailsAnalyzed: 658,
        bestModel: 'SVM (Linear, LinearSVC)',
        lastResult: {
          type: 'email',
          prediction: 'safe',
          confidence: 0.945,
          timestamp: new Date(),
        },
      }
    }
  },

  async getModelPerformance() {
    return mockLeaderboard
  },
}

export default {
  emailApi,
  urlApi,
  smsApi,
  dashboardApi,
}
