# ThreatLens AI - Frontend

A modern React-based web application for AI-powered phishing detection and URL analysis.

## Features

- **Email Analyzer**: Detect phishing emails using trained ML models
- **URL Analyzer**: Check URLs for malicious content and phishing patterns
- **Dashboard**: View comprehensive analytics and model performance metrics
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Analysis**: Get instant predictions with confidence scores
- **Model Leaderboard**: Compare performance metrics across 5 different ML models

## Tech Stack

- **Frontend Framework**: React 18
- **Routing**: React Router v6
- **Styling**: Tailwind CSS
- **UI Icons**: Lucide React
- **Charts & Graphs**: Recharts
- **HTTP Client**: Axios
- **Build Tool**: Vite

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ResultCard.jsx
│   │   └── LeaderboardTable.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── EmailAnalyzer.jsx
│   │   ├── URLAnalyzer.jsx
│   │   └── Dashboard.jsx
│   ├── services/
│   │   └── api.js (API integration)
│   ├── hooks/
│   │   └── useAnalysis.js (Custom React hooks)
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── index.html
```

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Building for Production

```bash
npm run build
npm run preview
```

## Components Overview

### Navbar
- Navigation links to all pages
- GitHub profile link
- Mobile-responsive hamburger menu
- Active route highlighting

### Home Page
- Hero section with call-to-action buttons
- Feature cards highlighting Email, URL, and Dashboard tools
- Statistics section
- Compelling CTA section

### Email Analyzer
- Textarea for email content input
- Real-time analysis
- Phishing/Safe prediction with confidence score
- Detailed findings display
- Model leaderboard
- Safety tips section

### URL Analyzer
- URL input field with validation
- Safe/malicious determination
- URL safety indicators
- Warning signs reference
- Analysis method explanation

### Dashboard
- Key statistics cards
- Bar chart: Model F1 Score comparison
- Line chart: Weekly scan trends
- Pie chart: Threat type distribution
- Bar chart: Model accuracy comparison
- Precision vs Recall comparison
- Detailed performance table

### Result Card
- Displays prediction (Phishing/Safe)
- Confidence score with visual progress bar
- Key findings list
- Color-coded based on threat level

### Leaderboard Table
- Ranks models by F1 score
- Shows all key metrics (Accuracy, Precision, Recall)
- Highlights best performing model
- Medal indicators for top 3

## API Integration

The app interfaces with a backend API with the following endpoints:

```
POST /api/email-check
  Body: { content: string }
  Response: { prediction, confidence, message, details, leaderboard }

POST /api/url-check
  Body: { url: string }
  Response: { prediction, confidence, message, details, leaderboard }

GET /api/stats
  Response: { totalScans, phishingDetected, legitEmailsAnalyzed, bestModel, lastResult }
```

The frontend includes fallback mock data for demonstration when the backend API is unavailable.

## Styling

All styling is done with **Tailwind CSS** with custom utility classes:

- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary action buttons
- `.card` - Reusable card component
- `.input-field` - Standard input styling

## Dark Mode Support

The app supports dark mode through Tailwind's dark mode utilities. Classes use `dark:` prefix for dark theme variants.

## Performance Optimization

- Lazy component loading with React Router
- Efficient state management with hooks
- Memoized components to prevent unnecessary re-renders
- Responsive charts with Recharts

## Future Enhancements

- User authentication and history tracking
- Advanced filtering on dashboard
- Export analysis reports as PDF
- Email integration for direct analysis
- Browser extension for on-the-fly URL checking
- Real-time threat intelligence updates
- Custom model training interface

## License

This project is part of the ThreatLens AI system - a comprehensive phishing detection platform.
