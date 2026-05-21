import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Mail, Globe, BarChart3, ArrowRight } from 'lucide-react'

function Home() {
  const [hoveredCard, setHoveredCard] = useState(null)

  const features = [
    {
      icon: Mail,
      title: 'Email Analysis',
      description: 'Detect phishing emails with AI-powered machine learning',
      link: '/email-analyzer',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Globe,
      title: 'URL Analysis',
      description: 'Identify malicious URLs and phishing links instantly',
      link: '/url-analyzer',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: BarChart3,
      title: 'Dashboard',
      description: 'View comprehensive statistics and model performance metrics',
      link: '/dashboard',
      color: 'from-orange-500 to-red-500',
    },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32 text-center">
        <div className="mb-6">
          <div className="inline-block">
            <span className="px-4 py-2 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 text-sm font-semibold">
              🛡️ Powered by Advanced AI
            </span>
          </div>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
          AI-Powered <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Phishing Detection</span>
        </h1>

        <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
          Analyze emails and URLs using state-of-the-art machine learning models. Stay protected from phishing attacks and cyber threats.
        </p>

        <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
          <Link to="/email-analyzer" className="btn-primary">
            📧 Analyze Email
          </Link>
          <Link to="/url-analyzer" className="btn-primary">
            🔗 Analyze URL
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <h2 className="text-4xl font-bold text-gray-900 dark:text-white text-center mb-16">
          Powerful Detection Tools
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, idx) => {
            const Icon = feature.icon
            return (
              <Link
                key={idx}
                to={feature.link}
                onMouseEnter={() => setHoveredCard(idx)}
                onMouseLeave={() => setHoveredCard(null)}
                className="card group cursor-pointer"
              >
                <div
                  className={`w-16 h-16 rounded-lg bg-gradient-to-br ${feature.color} p-3 mb-4 group-hover:scale-110 transition-transform`}
                >
                  <Icon className="w-full h-full text-white" />
                </div>

                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-indigo-600 transition-colors">
                  {feature.title}
                </h3>

                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {feature.description}
                </p>

                <div className="flex items-center gap-2 text-indigo-600 font-semibold group-hover:gap-3 transition-all">
                  Get Started
                  <ArrowRight className={`w-4 h-4 ${hoveredCard === idx ? 'translate-x-2' : ''} transition-transform`} />
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="grid md:grid-cols-4 gap-8">
          {[
            { label: 'Models Trained', value: '5+' },
            { label: 'Best Accuracy', value: '98.45%' },
            { label: 'Emails Analyzed', value: '82K+' },
            { label: 'Detection Rate', value: '99%' },
          ].map((stat, idx) => (
            <div key={idx} className="card text-center">
              <div className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-2">
                {stat.value}
              </div>
              <div className="text-gray-600 dark:text-gray-400 font-semibold">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl text-white text-center">
        <h2 className="text-4xl font-bold mb-6">Ready to Secure Your Inbox?</h2>
        <p className="text-lg mb-8 opacity-90">
          Start analyzing suspicious emails and URLs right now with ThreatLens AI
        </p>
        <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
          <Link to="/email-analyzer" className="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Analyze Email
          </Link>
          <Link to="/dashboard" className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-indigo-600 transition-colors">
            View Dashboard
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home
