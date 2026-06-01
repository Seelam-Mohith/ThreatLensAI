import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import EmailAnalyzer from './pages/EmailAnalyzer'
import URLAnalyzer from './pages/URLAnalyzer'
import Dashboard from './pages/Dashboard'
import AnimatedBackground from './components/AnimatedBackground'

function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen">
        <AnimatedBackground />
        <div className="relative z-10 min-h-screen bg-gradient-to-br dark:from-gray-950 dark:to-gray-900 bg-transparent backdrop-blur-sm">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/email-analyzer" element={<EmailAnalyzer />} />
              <Route path="/url-analyzer" element={<URLAnalyzer />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
