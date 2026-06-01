import { useState } from 'react'
import { Mail, AlertCircle } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultCard from '../components/ResultCard'
import LeaderboardTable from '../components/LeaderboardTable'
import { useEmailAnalysis } from '../hooks/useAnalysis'
import { emailApi } from '../services/api'

function EmailAnalyzer() {
  const [emailContent, setEmailContent] = useState('')
  const { loading, error, result, analyze } = useEmailAnalysis()

  const handleAnalyze = async () => {
    if (!emailContent.trim()) {
      alert('Please enter email content to analyze')
      return
    }
    await analyze(emailContent, emailApi.checkEmail)
  }

  const handleClear = () => {
    setEmailContent('')
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <div className="flex items-center gap-3 mb-4">
          <Mail className="w-10 h-10 text-indigo-600" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">Email Analyzer</h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Paste email content below to detect phishing attempts and get detailed analysis
        </p>
      </div>

      {/* Input Section */}
      <div className="card mb-8">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Email Content
        </label>
        <textarea
          value={emailContent}
          onChange={(e) => setEmailContent(e.target.value)}
          placeholder="Paste the email content here... Include subject line, body, and any links or attachments."
          className="input-field min-h-48 resize-none focus:ring-2 focus:ring-indigo-500"
          disabled={loading}
        />

        <div className="flex gap-4 mt-6">
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze Email'}
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
            Your email content is analyzed using our detection engine. No data is stored or sent to external servers.
          </p>
        </div>
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner message="Analyzing email... Please wait" />}

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

      {/* Leaderboard */}
      {result && result.leaderboard && (
        <LeaderboardTable
          data={result.leaderboard}
          highlight="SVM (Linear, LinearSVC)"
        />
      )}

      {/* Tips Section */}
      {!result && !loading && (
        <div className="card mt-12 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Quick Tips</h3>
          <ul className="space-y-3 text-gray-700 dark:text-gray-300">
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span>Look for grammar errors and suspicious sender addresses</span>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span>Check for urgent language demanding immediate action</span>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span>Hover over links to see the actual URL destination</span>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-600">•</span>
              <span>Never click links or download attachments from unknown senders</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default EmailAnalyzer
