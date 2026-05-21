import { useState } from 'react'

export function useEmailAnalysis() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const analyze = async (content, apiFunction) => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiFunction(content)
      setResult(data)
      return data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, result, analyze }
}

export function useUrlAnalysis() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const analyze = async (url, apiFunction) => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiFunction(url)
      setResult(data)
      return data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, result, analyze }
}
