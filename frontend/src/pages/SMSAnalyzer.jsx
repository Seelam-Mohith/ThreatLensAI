import { useState } from 'react'
import { MessageSquare, AlertCircle } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultCard from '../components/ResultCard'
import LeaderboardTable from '../components/LeaderboardTable'
import { useEmailAnalysis } from '../hooks/useAnalysis'
import { smsApi } from '../services/api'

function SMSAnalyzer() {
  const [smsContent, setSmsContent] = useState('')
  const { loading, error, result, analyze } = useEmailAnalysis()

  const handleAnalyze = async () => {
    if (!smsContent.trim()) {
      alert('Please enter SMS content to analyze')
      return
    }
    await analyze(smsContent, smsApi.checkSms)
  }

  const handleClear = () => {
    setSmsContent('')
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-12">
        <div className="flex items-center gap-3 mb-4">
          <MessageSquare className="w-10 h-10 text-indigo-600" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">SMS Analyzer</h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Paste or type SMS content below to detect scam or phishing attempts.
        </p>
      </div>

      <div className="card mb-8">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          SMS Content
        </label>
        <textarea
          value={smsContent}
          onChange={(e) => setSmsContent(e.target.value)}
          placeholder="Paste the SMS content here... Include sender info, body, and any short links."
          className="input-field min-h-32 resize-none focus:ring-2 focus:ring-indigo-500"
          disabled={loading}
        />

        <div className="flex gap-4 mt-6">
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze SMS'}
          </button>
          <button
            onClick={handleClear}
            disabled={loading}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear
          </button>
        </div>

        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-700 dark:text-blue-300">
            SMS content is analyzed locally with our detection engine. No data is stored.
          </p>
        </div>
      </div>

      {loading && <LoadingSpinner message="Analyzing SMS... Please wait" />}

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
      
      <ResultCard result={result} isLoading={loading} />

      {result && result.leaderboard && (
        <LeaderboardTable data={result.leaderboard} highlight="SVM (Linear, LinearSVC)" />
      )}
    </div>
  )
}

export default SMSAnalyzer
