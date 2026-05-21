import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, Activity, Mail, AlertCircle } from 'lucide-react'
import { dashboardApi } from '../services/api'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [performanceData, setPerformanceData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsData = await dashboardApi.getStats()
        const perfData = await dashboardApi.getModelPerformance()
        setStats(statsData)

        // Transform performance data for charts
        setPerformanceData(
          perfData.map((item) => ({
            model: item.model.split('(')[0].trim().substring(0, 12),
            fullModel: item.model,
            f1: parseFloat((item.f1 * 100).toFixed(2)),
            accuracy: parseFloat((item.accuracy * 100).toFixed(2)),
            precision: parseFloat((item.precision * 100).toFixed(2)),
            recall: parseFloat((item.recall * 100).toFixed(2)),
          }))
        )
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Mock data for scan trends
  const scanTrends = [
    { date: 'Mon', scans: 120, detected: 8 },
    { date: 'Tue', scans: 145, detected: 12 },
    { date: 'Wed', scans: 98, detected: 5 },
    { date: 'Thu', scans: 167, detected: 18 },
    { date: 'Fri', scans: 189, detected: 22 },
    { date: 'Sat', scans: 156, detected: 14 },
    { date: 'Sun', scans: 112, detected: 9 },
  ]

  const threatTypes = [
    { name: 'Phishing', value: 45, color: '#ef4444' },
    { name: 'Malware', value: 25, color: '#f59e0b' },
    { name: 'Spam', value: 20, color: '#eab308' },
    { name: 'Other', value: 10, color: '#6b7280' },
  ]

  const StatCard = ({ icon: Icon, title, value, subtitle, color }) => (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm font-semibold mb-2">{title}</p>
          <p className={`text-4xl font-bold ${color}`}>{value}</p>
          {subtitle && <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color.replace('text', 'bg')}/10`}>
          <Icon className={`w-8 h-8 ${color}`} />
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="w-12 h-12 text-indigo-600 animate-spin-slow mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Overview of threat detection and model performance analytics
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={Activity}
          title="Total Scans"
          value={stats?.totalScans || 0}
          subtitle="All time"
          color="text-blue-600"
        />
        <StatCard
          icon={AlertCircle}
          title="Threats Detected"
          value={stats?.phishingDetected || 0}
          subtitle="This month"
          color="text-red-600"
        />
        <StatCard
          icon={Mail}
          title="Emails Analyzed"
          value={stats?.legitEmailsAnalyzed || 0}
          subtitle="Safe emails"
          color="text-green-600"
        />
        <StatCard
          icon={TrendingUp}
          title="Best Model"
          value="SVM"
          subtitle="98.45% F1 Score"
          color="text-indigo-600"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Model Performance Comparison */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Model F1 Score Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="model" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Bar dataKey="f1" fill="#6366f1" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Detection Rate Trend */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Weekly Scan Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scanTrends} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="scans" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1' }} />
              <Line
                type="monotone"
                dataKey="detected"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ fill: '#ef4444' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid md:grid-cols-3 gap-8 mb-8">
        {/* Accuracy Comparison */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center">Model Accuracy</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={performanceData} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Bar dataKey="accuracy" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Threat Type Distribution */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center">Threat Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={threatTypes}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
              >
                {threatTypes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {threatTypes.map((threat, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: threat.color }} />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {threat.name}: {threat.value}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Precision vs Recall */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center">Precision vs Recall</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart
              data={performanceData.slice(0, 4)}
              margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="model" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Legend />
              <Bar dataKey="precision" fill="#10b981" radius={[8, 0, 0, 0]} />
              <Bar dataKey="recall" fill="#f59e0b" radius={[8, 0, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model Details Table */}
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
                <tr
                  key={idx}
                  className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <td className="py-3 px-4 font-semibold text-gray-800 dark:text-gray-200">{row.fullModel}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-block px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200 font-semibold">
                      {row.f1.toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{row.accuracy.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{row.precision.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{row.recall.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-block px-3 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200 text-xs font-semibold">
                      ✓ Active
                    </span>
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
