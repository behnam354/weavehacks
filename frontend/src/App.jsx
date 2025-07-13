import React from 'react';
import ArtisticQRGenerator from './ArtisticQRGenerator';

// Error boundary component to catch any errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-8">
          <h1 className="text-4xl font-bold text-center mb-4 text-red-400">
            🚨 Component Error 🚨
          </h1>
          <div className="max-w-2xl mx-auto bg-gray-800 p-6 rounded-lg">
            <p className="text-red-300 mb-4">
              There was an error loading the ArtisticQRGenerator component:
            </p>
            <pre className="bg-gray-900 p-4 rounded text-sm overflow-auto">
              {this.state.error?.toString()}
            </pre>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <ArtisticQRGenerator />
    </ErrorBoundary>
  );
}

export default App;
