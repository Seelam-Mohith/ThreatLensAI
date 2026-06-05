import { Sparkles, ShieldCheck } from 'lucide-react'

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

  return !EXPLANATION_FALLBACK_MARKERS.some((marker) => trimmed.includes(marker))
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
    const intro = normalizedSummary.slice(0, numberedMatches[0].index).trim()
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

function AIInsightCard({ result, artifactLabel }) {
  const showExplanation = hasUsableExplanation(result?.explanation)

  if (!showExplanation) {
    return null
  }

  const explanation = parseExplanation(result?.explanation || '')
  const summaryContent = buildSummaryPoints(explanation.summary)
  const explanationBadge = result?.explanationSource === 'gemini'
    ? 'Gemini Insight'
    : result?.explanationSource === 'local_fallback'
      ? 'Local Fallback'
      : 'Analysis Insight'
  const confidenceSummary = typeof result?.confidence === 'number'
    ? `This ${artifactLabel.toLowerCase()} is ${result?.isPhishing ? 'flagged as suspicious' : 'considered safe'} with a confidence score of ${(result.confidence * 100).toFixed(1)}%.`
    : ''

  return (
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
              Additional context generated from the scan result and {artifactLabel.toLowerCase()} content.
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
  )
}

export default AIInsightCard
