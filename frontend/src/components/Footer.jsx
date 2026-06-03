import { Github, Mail, Shield } from 'lucide-react'

function Footer() {
  return (
    <footer className="mt-16 border-t border-white/10 bg-gray-950/70 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div className="max-w-xl">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 p-2 shadow-lg">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">QuantShield</h3>
                <p className="text-sm text-gray-400">Threat Analysis Platform</p>
              </div>
            </div>

            <p className="mt-4 text-sm leading-6 text-gray-400">
              Analyze emails, URLs, and messages for phishing signals with a blend of
              machine learning insights and guided security explanations.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-gray-300">
                Contact
              </h4>
              <a
                href="mailto:seelammohith2222@gmail.com"
                className="mt-3 flex items-center gap-3 text-sm text-gray-400 transition-colors hover:text-indigo-300"
              >
                <Mail className="h-4 w-4" />
                <span>seelammohith2222@gmail.com</span>
              </a>
            </div>

            <div>
              <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-gray-300">
                Creator
              </h4>
              <a
                href="https://github.com/Seelam-Mohith"
                target="_blank"
                rel="noreferrer"
                className="mt-3 flex items-center gap-3 text-sm text-gray-400 transition-colors hover:text-indigo-300"
              >
                <Github className="h-4 w-4" />
                <span>github.com/Seelam-Mohith</span>
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t border-white/10 pt-4 text-xs text-gray-500">
          Built by Seelam Mohith for cybersecurity-focused threat analysis.
        </div>
      </div>
    </footer>
  )
}

export default Footer
