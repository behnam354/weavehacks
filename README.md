# Artistic QR Code Generator (WeaveHacks)

This project is a multi-agent, sponsor-integrated artistic QR code generator built for the WeaveHacks hackathon. It uses a React frontend to simulate agent workflows, protocol messages, and artistic QR code creation.

## Features
- Multi-agent orchestration (Crew AI)
- Sponsor tool simulation: Weave, Exa, BrowserBase, Google Cloud, Fly.io
- Artistic QR code generation with selectable styles
- Live agent logs, protocol messages, and workflow trace

## Getting Started

### 1. Clone the repository
```bash
git clone <repo-url>
cd weavehacks
```

### 2. Install dependencies and run locally
This project uses [Vite](https://vitejs.dev/) for fast React development. If you don't have Vite, install it globally or use `npm create vite@latest`.

#### If starting from scratch:
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

#### Or, if the `frontend` folder already exists:
```bash
cd frontend
npm install
```

### 3. Add the ArtisticQRGenerator component
Place the provided `ArtisticQRGenerator.jsx` file in `frontend/src/`.

### 4. Use the component
Edit `frontend/src/App.jsx` to use the `ArtisticQRGenerator` component:
```jsx
import ArtisticQRGenerator from './ArtisticQRGenerator';

function App() {
  return <ArtisticQRGenerator />;
}

export default App;
```

### 5. Run the app
```bash
npm run dev
```

Visit the local URL (usually http://localhost:5173) to use the app.

## Testing
- The app is self-contained and can be tested by running locally and interacting with the UI.
- All sponsor integrations are simulated for demo purposes.

## License
MIT
