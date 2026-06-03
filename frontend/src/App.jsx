import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import AnimatedBackground from './components/AnimatedBackground'
import LoadingSpinner from './components/LoadingSpinner'

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'))
const EmailAnalyzer = lazy(() => import('./pages/EmailAnalyzer'))
const URLAnalyzer = lazy(() => import('./pages/URLAnalyzer'))
const SMSAnalyzer = lazy(() => import('./pages/SMSAnalyzer'))
const Dashboard = lazy(() => import('./pages/Dashboard'))

function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen bg-black">
        <AnimatedBackground />
        <div className="relative z-10 min-h-screen">
          <Navbar />
          <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><LoadingSpinner /></div>}>
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/email-analyzer" element={<EmailAnalyzer />} />
                <Route path="/url-analyzer" element={<URLAnalyzer />} />
                <Route path="/sms-analyzer" element={<SMSAnalyzer />} />
                <Route path="/dashboard" element={<Dashboard />} />
              </Routes>
            </main>
          </Suspense>
          <Footer />
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
