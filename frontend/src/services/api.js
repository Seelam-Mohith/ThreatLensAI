import axios from 'axios'

const API_BASE_URL = 'https://quant-shield-backend.vercel.app'

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
      const response = await apiClient.post('/api/email-check', { content: emailContent })
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
      const response = await apiClient.post('/api/url-check', { url })
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
      const isPhishing = Math.random() > 0.8
      return {
        isPhishing,
        confidence: 0.82 + Math.random() * 0.18,
        message: isPhishing
          ? 'This URL may be malicious or designed to phish for credentials.'
          : 'This URL appears to be safe to visit.',
        explanation: isPhishing
          ? 'This URL shows phishing-like link patterns such as account-action wording, shortened link behavior, or other suspicious structure.'
          : 'This URL does not show strong phishing patterns in the fallback demo analysis.',
        explanationSource: 'demo',
        explanationNote: 'Backend API unavailable.',
        details: [
          isPhishing ? 'Domain age suspicious' : 'Verified domain',
          isPhishing ? 'SSL certificate issues' : 'Valid SSL certificate',
          isPhishing ? 'Known phishing pattern' : 'No known threats',
        ],
        leaderboard: mockLeaderboard,
        modelUsed: 'Demo Analysis Engine',
      }
    }
  },
}

export const smsApi = {
  async checkSms(smsContent) {
    try {
      const normalizedSmsContent = String(smsContent || '').toLowerCase()
      const response = await apiClient.post(
        '/api/sms-check',
        {
          content: smsContent
        }
      )

      const predictionValue = String(
        response.data.prediction ?? response.data.classification ?? ''
      ).trim().toLowerCase()
      const isPhishing = (
        response.data.isPhishing === true ||
        response.data.is_phishing === true ||
        predictionValue === 'spam' ||
        predictionValue === 'phishing' ||
        predictionValue === 'malicious' ||
        predictionValue === 'scam'
      )
      const confidenceValue = Number(response.data.confidence)
      const suspiciousSignals = [
        'bit.ly',
        'tinyurl',
        'shorturl',
        '.xyz',
        '.top',
        '.click',
        '.ru',
        'verify',
        'confirm',
        'urgent',
        'otp',
        'password',
        'bank',
        'account',
        'refund',
        'winner',
        'prize',
        'free money',
        'scam',
      ]
      const looksSuspicious = suspiciousSignals.some((signal) =>
        normalizedSmsContent.includes(signal)
      )
      const displayAsPhishing = isPhishing || (
        !isPhishing &&
        looksSuspicious &&
        ['ham', 'safe', 'legit', 'legitimate', 'normal', 'unknown', ''].includes(predictionValue)
      )

      return {
        isPhishing: displayAsPhishing,
        confidence: Number.isFinite(confidenceValue) && confidenceValue > 0
          ? confidenceValue
          : displayAsPhishing
            ? 0.88
          : null,
        message: displayAsPhishing
          ? (response.data.message && !/legitimate|safe/i.test(response.data.message)
              ? response.data.message
              : 'This SMS looks suspicious and may be part of a phishing/scam.')
          : (response.data.message || (
            isPhishing
            ? 'This SMS looks suspicious and may be part of a phishing/scam.'
            : 'This SMS appears legitimate.'
          )),
        explanation: response.data.ai_explanation || '',
        explanationSource: response.data.explanation_source || 'unknown',
        explanationNote: displayAsPhishing && !isPhishing
          ? 'Frontend safety heuristic reinforced the SMS result because the content contains obvious scam indicators.'
          : response.data.explanation_note || '',
        details: displayAsPhishing && !isPhishing
          ? [
            'Suspicious SMS keywords or link patterns detected on the frontend.',
            ...(response.data.details || []).slice(0, 2),
          ]
          : response.data.details || [],
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
      const response = await apiClient.get('/api/stats')
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

export const networkApi = {
  async analyzeCapture(file) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post('/api/network-check', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      return {
        isIntrusion: response.data.prediction === 'intrusion',
        confidence: response.data.confidence || 0,
        message: response.data.message || '',
        modelUsed: response.data.model_used || 'Random Forest Portscan IDS',
        filename: response.data.filename || file.name,
        flowsAnalyzed: response.data.flows_analyzed || 0,
        featureColumns: response.data.feature_columns || [],
        featureLogs: response.data.feature_logs || [],
        flowResults: response.data.flow_results || [],
      }
    } catch (error) {
      console.warn('API call failed, using mock network data:', error.message)

      return {
        isIntrusion: true,
        confidence: 0.87,
        message:
          'The uploaded capture shows suspicious network flow behavior in this demo fallback.',
        modelUsed: 'Demo Network IDS Engine',
        filename: file.name,
        flowsAnalyzed: 3,
        featureColumns: ['Flow Duration', 'Total Fwd Packets', 'Flow Bytes/s'],
        featureLogs: [
          'Fallback analysis used because the backend API was unavailable.',
          'Feature alignment completed against the demo schema.',
        ],
        flowResults: [
          {
            flow_id: '10.0.0.45:51514 -> 185.220.101.4:443 (TCP)',
            source: '10.0.0.45',
            destination: '185.220.101.4',
            source_port: 51514,
            destination_port: 443,
            protocol: 'TCP',
            prediction: 'intrusion',
            confidence: 0.91,
            packet_count: 14,
            duration_seconds: 3.42,
          },
          {
            flow_id: '192.168.1.24:60822 -> 172.217.160.78:443 (TCP)',
            source: '192.168.1.24',
            destination: '172.217.160.78',
            source_port: 60822,
            destination_port: 443,
            protocol: 'TCP',
            prediction: 'safe',
            confidence: 0.94,
            packet_count: 21,
            duration_seconds: 8.11,
          },
        ],
      }
    }
  },
}

export default {
  emailApi,
  urlApi,
  smsApi,
  dashboardApi,
  networkApi,
}
