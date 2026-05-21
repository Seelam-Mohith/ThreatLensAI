import { Loader } from 'lucide-react'

function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader className="w-12 h-12 text-indigo-600 animate-spin-slow mb-4" />
      <p className="text-gray-600 dark:text-gray-400 text-lg font-semibold">{message}</p>
    </div>
  )
}

export default LoadingSpinner
