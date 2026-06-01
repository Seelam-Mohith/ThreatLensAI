# Quick Start Guide - QuantShield Frontend

## Prerequisites

- Node.js 16+ 
- npm or yarn package manager
- Backend API running on `http://localhost:5000` (optional for demo)

## Getting Started

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The app will open at `http://localhost:3000`

### 3. Build for Production
```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/            # Reusable UI components
│   │   ├── Navbar.jsx         # Navigation bar with routing
│   │   ├── LoadingSpinner.jsx # Loading indicator
│   │   ├── ResultCard.jsx     # Analysis result display
│   │   └── LeaderboardTable.jsx # Model performance table
│   │
│   ├── pages/                 # Full page components
│   │   ├── Home.jsx           # Landing page with hero section
│   │   ├── EmailAnalyzer.jsx  # Email phishing detection
│   │   ├── URLAnalyzer.jsx    # URL safety check
│   │   └── Dashboard.jsx      # Analytics and charts
│   │
│   ├── services/              # API communication
│   │   └── api.js             # Axios client & API functions
│   │
│   ├── hooks/                 # Custom React hooks
│   │   └── useAnalysis.js     # Analysis state management
│   │
│   ├── App.jsx                # Main app with routing
│   ├── main.jsx               # Entry point
│   └── index.css              # Global styles & Tailwind
│
├── index.html                 # HTML template
├── package.json               # Dependencies
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # Tailwind CSS config
├── postcss.config.js          # PostCSS config
└── README.md                  # Full documentation
```

## Available Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | Home | Landing page with overview |
| `/email-analyzer` | EmailAnalyzer | Analyze email content for phishing |
| `/url-analyzer` | URLAnalyzer | Check URL safety |
| `/dashboard` | Dashboard | View analytics and model performance |

## Key Technologies

| Technology | Purpose |
|-----------|---------|
| **React 18** | UI framework with hooks |
| **React Router v6** | Client-side routing |
| **Tailwind CSS** | Utility-first CSS styling |
| **Vite** | Fast build tool & dev server |
| **Axios** | HTTP client for API calls |
| **Recharts** | Data visualization charts |
| **Lucide React** | SVG icons |

## Component Communication Flow

```
App (routing context)
├── Navbar (navigation)
└── [Page Routes]
    ├── Home (landing)
    ├── EmailAnalyzer
    │   ├── useEmailAnalysis (hook)
    │   ├── emailApi.checkEmail (service)
    │   ├── LoadingSpinner
    │   ├── ResultCard
    │   └── LeaderboardTable
    ├── URLAnalyzer
    │   ├── useUrlAnalysis (hook)
    │   ├── urlApi.checkUrl (service)
    │   ├── LoadingSpinner
    │   ├── ResultCard
    │   └── LeaderboardTable
    └── Dashboard (charts & stats)
```

## API Integration Example

The app uses base API URL: `http://localhost:5000/api`

### Email Check Endpoint
```javascript
const result = await emailApi.checkEmail(emailContent);
// Returns: { isPhishing, confidence, message, details, leaderboard }
```

### URL Check Endpoint
```javascript
const result = await urlApi.checkUrl(url);
// Returns: { isPhishing, confidence, message, details, leaderboard }
```

### Dashboard Stats Endpoint
```javascript
const stats = await dashboardApi.getStats();
// Returns: { totalScans, phishingDetected, legitEmailsAnalyzed, bestModel, lastResult }
```

## Key Features

- **Responsive Design** - Works on all devices (mobile, tablet, desktop)
- **Dark Mode Ready** - Tailwind dark mode support
- **Loading States** - Spinner component for better UX
- **Error Handling** - Graceful error messages
- **Mock Data Fallback** - Works without backend API
- **Model Leaderboard** - Compare multiple models
- **Real-time Charts** - Interactive data visualization
- **Mobile Navigation** - Responsive hamburger menu

## Custom Tailwind Components

```css
/* Primary Action Button */
<button className="btn-primary">Click Me</button>

/* Secondary Button */
<button className="btn-secondary">Cancel</button>

/* Card Component */
<div className="card">Content</div>

/* Input Field */
<input className="input-field" />

/* Small Button */
<button className="btn-small">Action</button>
```

## Dark Mode Usage

Tailwind dark mode is enabled. Use `dark:` prefix:

```jsx
<div className="bg-white dark:bg-gray-800">
  Content adapts to dark theme
</div>
```

## Dashboard Charts

- **Bar Chart**: Model F1 Score comparison
- **Line Chart**: Weekly scan trends
- **Pie Chart**: Threat type distribution
- **Bar Chart**: Model accuracy metrics
- **Bar Chart**: Precision vs Recall

## Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- --port 3001
```

### API not connecting
- Check backend server is running on `http://localhost:5000`
- Frontend has mock data fallback for demo purposes
- Check browser console for detailed errors

### Tailwind styles not applied
```bash
# Rebuild Tailwind
npm run build
```

### Dependencies issues
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

## 🔐 Environment Variables

Create `.env.local` from `.env.example`:

```
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENABLE_DARK_MODE=true
VITE_ENABLE_CHARTS=true
```

## Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

## Component Exports

All components are functional and use React hooks:

```javascript
// Functional components
export default ComponentName

// Custom hooks
export function useAnalysisHook() { ... }

// API services
export const emailApi = { ... }
export const urlApi = { ... }
export const dashboardApi = { ... }
```

## Learning Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Recharts](https://recharts.org)
- [Vite Guide](https://vitejs.dev)

## Next Steps

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Open browser: `http://localhost:3000`
4. Test email/URL analyzers with sample data
5. Check dashboard for analytics
6. Connect backend API when ready

Enjoy!
