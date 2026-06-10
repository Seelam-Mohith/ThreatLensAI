import { useState } from 'react'
import { Globe, AlertCircle, Check } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultCard from '../components/ResultCard'
import AIInsightCard from '../components/AIInsightCard'
import { useUrlAnalysis } from '../hooks/useAnalysis'
import { urlApi } from '../services/api'

function URLAnalyzer() {
  const [url, setUrl] = useState('')
  const { loading, error, result, analyze } = useUrlAnalysis()

  const handleAnalyze = async () => {
    if (!url.trim()) {
      alert('Please enter a URL to analyze')
      return
    }
    await analyze(url, urlApi.checkUrl)
  }

  const handleClear = () => {
    setUrl('')
  }

  const isValidUrl = (urlString) => {
    try {
      new URL(urlString)
      return true
    } catch {
      return false
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <div className="flex items-center gap-3 mb-4">
          <Globe className="w-10 h-10 text-indigo-600" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">URL Analyzer</h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Check if a URL is safe or potentially malicious using our analysis engine
        </p>
      </div>

      {/* Input Section */}
      <div className="card mb-8">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          URL to Analyze
        </label>
        <div className="flex gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter full URL (e.g., https://example.com)"
            className="input-field flex-1"
            disabled={loading}
            onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
          />
          {url && isValidUrl(url) && (
            <div className="flex items-center px-3 text-green-600 dark:text-green-400">
              <Check className="w-4 h-4" />
            </div>
          )}
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={handleAnalyze}
            disabled={loading || !url.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze URL'}
          </button>
          <button
            onClick={handleClear}
            disabled={loading}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear
          </button>
        </div>

        {/* Info Note */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Analysis is performed safely without visiting the URL. The frontend sends the URL text to the backend classifier, which returns a phishing or legitimate prediction and confidence score.
          </p>
        </div>
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner message="Analyzing URL... Please wait" />}

      {/* Error State */}
      {error && (
        <div className="card mb-8 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500">
          <div className="flex gap-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-red-800 dark:text-red-200">Analysis Error</h3>
              <p className="text-red-700 dark:text-red-300 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Result Card */}
      <ResultCard result={result} isLoading={loading} />
      <AIInsightCard result={result} artifactLabel="URL" />

      {/* Safety Tips Section */}
      <div className="mt-12 grid md:grid-cols-2 gap-8">
        <div className="card bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Safe URL Indicators</h3>
          <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li>• HTTPS protocol (not HTTP)</li>
            <li>• Well-known domain names</li>
            <li>• Matching domain in URL and displayed</li>
            <li>• Valid SSL certificate</li>
            <li>• Old established domain</li>
          </ul>
        </div>

        <div className="card bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Warning Signs</h3>
          <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li>• Shortened or obfuscated URLs</li>
            <li>• Suspicious TLDs (.tk, .ml, etc.)</li>
            <li>• Recently registered domains</li>
            <li>• Misspelled domain names</li>
            <li>• Excessive redirects</li>
          </ul>
        </div>
      </div>

      {/* Analysis Tips */}
      {!result && !loading && (
        <div className="card mt-12 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Analysis Methods</h3>
          <ul className="space-y-3 text-gray-700 dark:text-gray-300">
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span><strong>Model Inference:</strong> Sends the URL string to the trained backend classifier</span>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span><strong>Confidence Score:</strong> Shows how strongly the model supports the prediction</span>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span><strong>Fallback Logic:</strong> Uses pattern checks only if the trained model is unavailable</span>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span><strong>Safe Handling:</strong> Analyzes the URL text without opening the destination</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default URLAnalyzer
