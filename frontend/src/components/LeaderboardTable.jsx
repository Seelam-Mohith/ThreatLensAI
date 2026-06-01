import { TrendingUp } from 'lucide-react'

function LeaderboardTable({ data, highlight }) {
  if (!data || data.length === 0) {
    return null
  }

  return (
    <div className="card mt-8">
      <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
        <TrendingUp className="w-5 h-5 text-indigo-600" />
        Model Performance Leaderboard
      </h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-200 dark:border-gray-700">
              <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Rank</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Model</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">F1 Score</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Accuracy</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Precision</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Recall</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`border-b border-gray-100 dark:border-gray-700 transition-colors ${
                  highlight === row.model
                    ? 'bg-indigo-50 dark:bg-indigo-900/30'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full font-semibold ${
                    idx === 0 ? 'bg-yellow-100 text-yellow-800' : idx === 1 ? 'bg-gray-100 text-gray-800' : idx === 2 ? 'bg-amber-100 text-amber-800' : 'bg-transparent text-gray-500'
                  }`}>
                    {idx + 1}
                  </span>
                </td>
                <td className="py-3 px-4 font-semibold text-gray-800 dark:text-gray-200">{row.model}</td>
                <td className="py-3 px-4 text-center">
                  <span className="inline-block px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200 font-semibold">
                    {(row.f1 * 100).toFixed(2)}%
                  </span>
                </td>
                <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">
                  {(row.accuracy * 100).toFixed(2)}%
                </td>
                <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">
                  {(row.precision * 100).toFixed(2)}%
                </td>
                <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">
                  {(row.recall * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-blue-700 dark:text-blue-300">
        <span className="font-semibold">Best Model:</span> {data[0]?.model} with {(data[0]?.f1 * 100).toFixed(2)}% F1 Score
      </div>
    </div>
  )
}

export default LeaderboardTable
