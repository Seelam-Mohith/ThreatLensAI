import { useState, useEffect } from 'react'
import { Activity } from 'lucide-react'
import LeaderboardTable from '../components/LeaderboardTable'
import { dashboardApi } from '../services/api'

function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [performanceData, setPerformanceData] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const s = await dashboardApi.getStats()
        const p = await dashboardApi.getModelPerformance()
        setStats(s)
        setPerformanceData(p || [])
      } catch (err) {
        console.error('Failed to load model statistics', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="w-12 h-12 text-indigo-600 animate-spin-slow mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading model statistics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Model Statistics</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">Inspect models and performance by analysis type</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Email Models</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Models trained for email phishing detection and their performance.</p>
          <LeaderboardTable data={performanceData} highlight="SVM (Linear, LinearSVC)" />
        </div>

        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">URL Models</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Models focused on URL and link threat detection.</p>
          <LeaderboardTable data={performanceData} highlight="XGBoost Classifier" />
        </div>

        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">SMS Models</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Models for SMS/scam detection (short messages and links).</p>
          <LeaderboardTable data={performanceData} highlight="Multinomial Naive Bayes" />
        </div>
      </div>

      <div className="card">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Detailed Model Performance</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Model</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">F1 Score</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Accuracy</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Precision</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Recall</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Status</th>
              </tr>
            </thead>
            <tbody>
              {performanceData?.map((row, idx) => (
                <tr key={idx} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="py-3 px-4 font-semibold text-gray-800 dark:text-gray-200">{row.model}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-block px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200 font-semibold">
                      {(row.f1 * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{(row.accuracy * 100).toFixed(2)}%</td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{(row.precision * 100).toFixed(2)}%</td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{(row.recall * 100).toFixed(2)}%</td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-block px-3 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200 text-xs font-semibold">Active</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
