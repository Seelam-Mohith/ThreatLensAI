import { useMemo, useState } from 'react'
import { Activity, AlertCircle, FileUp, Shield, Upload, Wifi } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { networkApi } from '../services/api'

function NetworkIDS() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const isValidCapture = (file) => {
    if (!file) return false
    const lowerName = file.name.toLowerCase()
    return lowerName.endsWith('.pcap') || lowerName.endsWith('.pcapng')
  }

  const handleFileSelection = (file) => {
    if (!isValidCapture(file)) {
      setError('Please select a .pcap or .pcapng capture file.')
      setSelectedFile(null)
      setResult(null)
      return
    }

    setError(null)
    setSelectedFile(file)
    setResult(null)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    handleFileSelection(event.dataTransfer.files?.[0])
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a capture file before analyzing.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const analysis = await networkApi.analyzeCapture(selectedFile)
      setResult(analysis)
    } catch (analysisError) {
      setError(analysisError.message || 'Network analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setResult(null)
    setError(null)
  }

  const summaryTone = useMemo(() => {
    if (!result) {
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200'
    }

    return result.isIntrusion
      ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-200'
      : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-200'
  }, [result])

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-4">
          <Wifi className="w-10 h-10 text-indigo-600" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">Network Intrusion Detection</h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl">
          Upload a `.pcap` or `.pcapng` capture to run the backend network IDS model and review the flow-level verdicts.
        </p>
      </div>

      <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-8">
        <section className="card">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Capture Analysis</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                The backend extracts flows, aligns features, and scores the capture with the trained model.
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleAnalyze}
                disabled={!selectedFile || loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                <Activity className="w-4 h-4" />
                {loading ? 'Analyzing...' : 'Analyze Capture'}
              </button>
              <button
                onClick={handleClear}
                disabled={loading && !selectedFile}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="grid xl:grid-cols-2 gap-6 items-start">
            <div className="space-y-4">
              <label
                htmlFor="pcap-upload"
                onDragOver={(event) => {
                  event.preventDefault()
                  setIsDragging(true)
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors cursor-pointer ${
                  isDragging
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                    : 'border-gray-300 dark:border-gray-600 bg-white/80 dark:bg-gray-800/50'
                }`}
              >
                <Upload className="w-10 h-10 text-indigo-600 mb-3" />
                <span className="text-base font-semibold text-gray-900 dark:text-white">
                  Drag and drop a `.pcap` or `.pcapng` file here
                </span>
                <span className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  or click to browse and attach a packet capture
                </span>
                <input
                  id="pcap-upload"
                  type="file"
                  accept=".pcap,.pcapng"
                  className="hidden"
                  onChange={(event) => handleFileSelection(event.target.files?.[0])}
                />
              </label>

              <div className="flex items-center gap-3 rounded-xl bg-gray-50 dark:bg-gray-700/40 px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                <FileUp className="w-4 h-4 text-indigo-600" />
                {selectedFile ? (
                  <span>
                    Selected file: <span className="font-semibold text-gray-900 dark:text-white">{selectedFile.name}</span>
                  </span>
                ) : (
                  <span>No capture selected yet.</span>
                )}
              </div>

              {error && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg flex gap-3 border border-red-200 dark:border-red-900/40">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              )}

              {loading && <LoadingSpinner message="Analyzing capture... Please wait" />}
            </div>

            <div className="rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-5 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5" />
                  <span className="font-semibold">Analysis Result</span>
                </div>
                <span className="text-sm bg-white/15 px-3 py-1 rounded-full">
                  {result?.filename || 'Waiting for upload'}
                </span>
              </div>

              <div className="p-5 space-y-5 bg-gray-50 dark:bg-gray-900/40 min-h-[260px]">
                {result ? (
                  <>
                    <div className={`rounded-xl p-4 font-semibold ${summaryTone}`}>
                      {result.isIntrusion ? 'Potential intrusion detected' : 'Traffic appears legitimate'}
                    </div>

                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{result.message}</p>

                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="rounded-xl bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700">
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Confidence</p>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                          {(result.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="rounded-xl bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700">
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Flows Analyzed</p>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">{result.flowsAnalyzed}</p>
                      </div>
                    </div>

                    <div className="rounded-xl bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700">
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Model Used</p>
                      <p className="font-medium text-gray-900 dark:text-white">{result.modelUsed}</p>
                    </div>
                  </>
                ) : (
                  <div className="flex h-full min-h-[220px] items-center justify-center text-center text-gray-500 dark:text-gray-400">
                    Upload a capture and run analysis to see the result here.
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        <aside className="space-y-8">
          <div className="card">
            <div className="flex items-center gap-3 mb-5">
              <Shield className="w-7 h-7 text-indigo-600" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Flow Verdicts</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Per-flow predictions returned by `/api/network-check`
                </p>
              </div>
            </div>

            {result?.flowResults?.length ? (
              <div className="space-y-3">
                {result.flowResults.map((flow) => {
                  const isIntrusion = flow.prediction === 'intrusion'
                  return (
                    <div
                      key={flow.flow_id}
                      className="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-4"
                    >
                      <div className="flex flex-col gap-2">
                        <div className="flex items-start justify-between gap-3">
                          <p className="text-sm font-semibold text-gray-900 dark:text-white break-all">
                            {flow.flow_id}
                          </p>
                          <span
                            className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold ${
                              isIntrusion
                                ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-200'
                                : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-200'
                            }`}
                          >
                            {isIntrusion ? 'Intrusion' : 'Safe'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {flow.source} → {flow.destination} · {flow.protocol} · {flow.packet_count} packets
                        </p>
                        <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>Confidence: {(flow.confidence * 100).toFixed(1)}%</span>
                          <span>Duration: {flow.duration_seconds.toFixed(3)}s</span>
                          <span>Ports: {flow.source_port} → {flow.destination_port}</span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="rounded-xl bg-gray-50 dark:bg-gray-800/50 p-6 text-sm text-gray-600 dark:text-gray-400">
                Once you upload a capture, we’ll list each analyzed flow here with its prediction and confidence.
              </div>
            )}
          </div>

          <div className="card bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Feature Alignment</h3>
            {result?.featureLogs?.length ? (
              <ul className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
                {result.featureLogs.map((log, index) => (
                  <li key={`${index}-${log}`} className="flex gap-3">
                    <span className="text-indigo-600">•</span>
                    <span>{log}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-700 dark:text-gray-300">
                The backend returns feature-alignment notes so you can see how the capture was matched to the
                training schema.
              </p>
            )}
          </div>

          {result?.featureColumns?.length ? (
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Aligned Feature Columns</h3>
              <div className="flex flex-wrap gap-2">
                {result.featureColumns.slice(0, 18).map((column) => (
                  <span
                    key={column}
                    className="px-3 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                  >
                    {column}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </aside>
      </div>
    </div>
  )
}

export default NetworkIDS
