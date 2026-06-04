import { useState } from 'react'
import { Mail, AlertCircle, Sparkles, ShieldCheck } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultCard from '../components/ResultCard'
import LeaderboardTable from '../components/LeaderboardTable'
import { useEmailAnalysis } from '../hooks/useAnalysis'
import { emailApi } from '../services/api'

const EXPLANATION_FALLBACK_MARKERS = [
  'AI explanation is currently unavailable.',
  'Classified as ',
]

function stripMarkdown(text) {
  return text.replace(/\*\*/g, '').replace(/^\*\s*/g, '').trim()
}

function hasUsableExplanation(explanation) {
  if (!explanation) {
    return false
  }

  const trimmed = explanation.trim()

  if (!trimmed) {
    return false
  }

  return !EXPLANATION_FALLBACK_MARKERS.some(
    (marker) => trimmed.includes(marker)
  )
}

function parseExplanation(explanation) {
  if (!explanation) {
    return { summary: '', sections: [] }
  }

  const lines = explanation
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  const sections = []
  const summaryLines = []
  let currentSection = null

  lines.forEach((line) => {
    const cleanLine = stripMarkdown(line)
    const isBullet = /^[*-]\s+/.test(line)
    const isSectionTitle = cleanLine.endsWith(':') && !isBullet

    if (isSectionTitle) {
      if (currentSection) {
        sections.push(currentSection)
      }

      currentSection = {
        title: cleanLine.slice(0, -1),
        items: [],
      }
      return
    }

    if (isBullet && currentSection) {
      currentSection.items.push(cleanLine.replace(/^[-*]\s+/, ''))
      return
    }

    if (currentSection) {
      currentSection.items.push(cleanLine)
      return
    }

    summaryLines.push(cleanLine)
  })

  if (currentSection) {
    sections.push(currentSection)
  }

  return {
    summary: summaryLines.join(' '),
    sections,
  }
}

function buildSummaryPoints(summary) {
  if (!summary) {
    return { intro: '', points: [] }
  }

  const normalizedSummary = summary.replace(/\s+/g, ' ').trim()
  const numberedMatches = [...normalizedSummary.matchAll(/\b\d+\.\s*/g)]

  if (numberedMatches.length > 0) {
    const intro = normalizedSummary
      .slice(0, numberedMatches[0].index)
      .trim()

    const points = numberedMatches.map((match, index) => {
      const start = (match.index ?? 0) + match[0].length
      const end = index + 1 < numberedMatches.length
        ? numberedMatches[index + 1].index
        : normalizedSummary.length

      return normalizedSummary.slice(start, end).trim()
    }).filter(Boolean)

    return { intro, points }
  }

  const parts = normalizedSummary
    .split(/(?<=[.!?])\s+/)
    .map((part) => part.trim())
    .filter(Boolean)

  return {
    intro: parts[0] || '',
    points: parts.slice(1),
  }
}

function EmailAnalyzer() {
  const [emailContent, setEmailContent] = useState('')
  const { loading, error, result, analyze } = useEmailAnalysis()
  const showExplanation = hasUsableExplanation(result?.explanation)
  const explanation = parseExplanation(showExplanation ? result?.explanation : '')
  const summaryContent = buildSummaryPoints(explanation.summary)
  const explanationBadge = result?.explanationSource === 'gemini'
    ? 'Gemini Insight'
    : result?.explanationSource === 'local_fallback'
      ? 'Local Fallback'
      : 'Analysis Insight'
  const confidenceSummary = typeof result?.confidence === 'number'
    ? `This email is ${result?.isPhishing ? 'flagged as phishing' : 'considered safe'} with a confidence score of ${(result.confidence * 100).toFixed(1)}%.`
    : ''

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
      {showExplanation && (
        <div className="card mt-6 border-l-4 border-indigo-500">
          <div className="flex items-start justify-between gap-4 border-b border-gray-200 dark:border-gray-700 pb-5">
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-300">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    AI Security Analysis
                  </h3>
                  <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
                    {explanationBadge}
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Additional context generated from the scan result and email content.
                </p>
                {result?.explanationNote && (
                  <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">
                    {result.explanationNote}
                  </p>
                )}
              </div>
            </div>

            <div className="hidden sm:flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-indigo-600 dark:bg-gray-800 dark:text-indigo-300">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </div>

          <div className="mt-6 space-y-5">
            {explanation.summary && (
              <div className="rounded-xl bg-gray-50 p-5 dark:bg-gray-800/60">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-indigo-500" />
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                    Summary
                  </p>
                </div>

                {summaryContent.intro && (
                  <p className="mt-4 text-base font-medium leading-7 text-gray-800 dark:text-gray-200">
                    {summaryContent.intro}
                  </p>
                )}

                {(confidenceSummary || summaryContent.points.length > 0) && (
                  <ul className="mt-4 space-y-3">
                    {confidenceSummary && (
                      <li className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                        <span className="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-500" />
                        <span className="leading-6">{confidenceSummary}</span>
                      </li>
                    )}
                    {summaryContent.points.map((point, index) => (
                      <li
                        key={`summary-${index}`}
                        className="flex items-start gap-3 text-gray-700 dark:text-gray-300"
                      >
                        <span className="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-500" />
                        <span className="leading-6">{point}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {explanation.sections.map((section) => (
              <div
                key={section.title}
                className="rounded-xl bg-gray-50 p-5 dark:bg-gray-800/60"
              >
                <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                  {section.title}
                </h4>

                <ul className="mt-4 space-y-3">
                  {section.items.map((item, index) => (
                    <li
                      key={`${section.title}-${index}`}
                      className="flex items-start gap-3 text-gray-700 dark:text-gray-300"
                    >
                      <span className="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-500" />
                      <span className="leading-6">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}

            {!explanation.summary && explanation.sections.length === 0 && (
              <div className="rounded-xl bg-gray-50 p-5 dark:bg-gray-800/60">
                <p className="text-base leading-7 text-gray-700 dark:text-gray-300">
                  {stripMarkdown(result.explanation)}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

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
