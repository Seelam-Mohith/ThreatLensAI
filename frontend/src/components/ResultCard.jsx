import { AlertCircle, CheckCircle, Zap } from 'lucide-react'

function ResultCard({ result, isLoading }) {
  if (isLoading) {
    return null
  }

  if (!result) {
    return null
  }

  const isPredicting = result.isPhishing === true
  const Icon = isPredicting ? AlertCircle : CheckCircle

  return (
    <div className={`card mt-8 border-l-4 ${isPredicting ? 'border-l-red-500' : 'border-l-green-500'}`}>
      <div className="flex items-start gap-4">
        <Icon className={`w-8 h-8 mt-1 flex-shrink-0 ${isPredicting ? 'text-red-500' : 'text-green-500'}`} />
        <div className="flex-1">
          <h3 className={`text-2xl font-bold ${isPredicting ? 'text-red-600' : 'text-green-600'}`}>
            {isPredicting ? '🚨 Phishing Detected' : '✓ Safe to Open'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {result.message || 'Analysis complete.'}
          </p>
        </div>
      </div>

      {/* Confidence Score */}
      {result.confidence && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-gray-700 dark:text-gray-300">Confidence Score</span>
            <span className="text-2xl font-bold text-indigo-600">{(result.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                isPredicting ? 'bg-red-500' : 'bg-green-500'
              }`}
              style={{ width: `${result.confidence * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Analysis Details */}
      {result.details && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Key Findings
          </h4>
          <ul className="space-y-2">
            {result.details.map((detail, idx) => (
              <li key={idx} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                {detail}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default ResultCard
