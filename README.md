# AgentQR

<p align="center">
  <img src="./backend/qr_code_art.png" alt="AgentQR Artistic QR Code" width="320" />
</p>

<h2 align="center"><i>QR Codes, reimagined by AI</i></h2>

---

# Artistic QR Code Generator (WeaveHacks)

## Tech Stack

**Languages:**
- Python 3.11+ (backend, agent orchestration, API)
- JavaScript (ES6+) (frontend, React)
- TypeScript (optionally supported in frontend)

**Frameworks & Libraries:**
- FastAPI (Python web framework for backend API)
- React (frontend UI framework)
- Vite (frontend build tool for React)
- Tailwind CSS (utility-first CSS framework for styling)
- CrewAI (multi-agent orchestration framework)
- OpenAI / Weights & Biases (W&B) LLM (LLM orchestration and logging)
- Replicate (AI model inference for artistic QR code generation)
- Weave (tracing, observability, and logging for agents)
- Lucide-react (icon library for React UI)
- requests (Python HTTP client for API calls)
- dotenv (environment variable management)

**APIs & External Services:**
- Replicate API (for generative AI QR code art)
- Exa API (semantic web search for brand/visual identity research)
- Browserbase API (web scraping for design/brand research)
- Weights & Biases (W&B) API (experiment tracking, logging, and observability)
- OpenAI API (LLM, via W&B inference endpoint)

**Cloud Platforms & Deployment:**
- Fly.io (cloud platform for deploying backend and frontend)
- Docker (containerization for deployment)
- Nginx (serving static frontend assets in production)

**Other Technologies:**
- PostCSS (CSS processing for Tailwind)
- Uvicorn (ASGI server for FastAPI)
- Pydantic (data validation in FastAPI)
- Git (version control)
- GitHub (repository hosting and collaboration)

**Databases:**
- None required for core functionality (all data is ephemeral or handled via APIs; could be extended with a database for user/session storage if needed)

This project is a multi-agent, sponsor-integrated artistic QR code generator built for the WeaveHacks hackathon. It uses a React frontend to simulate agent workflows, protocol messages, and artistic QR code creation.

## Features
- Multi-agent orchestration (Crew AI)
- Sponsor tool simulation: Weave, Exa, BrowserBase, Google Cloud, Fly.io
- Artistic QR code generation with selectable styles
- Live agent logs, protocol messages, and workflow trace

## Tailwind CSS Compatibility
**This project uses Tailwind CSS v3 for maximum compatibility with Vite and PostCSS.**
- The PostCSS config uses the classic plugin syntax:
  ```js
  module.exports = {
    plugins: [
      require('tailwindcss'),
      require('autoprefixer'),
    ],
  }
  ```
- If you upgrade to Tailwind v4+, you must update your PostCSS config and may encounter compatibility issues.

## Getting Started

### 1. Clone the repository
```bash
git clone <repo-url>
cd weavehacks
```

---

## Backend (Python + FastAPI + Weave)

> **Python 3.11 or above is required** for CrewAI and other dependencies. If you are using an older version, please upgrade your Python before proceeding.

### Setup

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the backend server
```bash
uvicorn main:app --reload
```
- The backend will be available at http://localhost:8000
- Health check: http://localhost:8000/health
- Trace endpoint: POST http://localhost:8000/trace

### Weave/W&B Integration
- The backend logs trace events to Weights & Biases (W&B) using the `wandb` Python SDK.
- Set the `WANDB_PROJECT` environment variable to change the project name (default: `weavehacks-demo`).
- You can view traces in your W&B dashboard.

---

## Frontend (React + Vite + Tailwind CSS)

### Install dependencies and run locally
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

## Deploying to Fly.io

### Quickstart: Deploy HelloFly Demo App
If you just want to try Fly.io, you can launch their demo app:

```bash
# Install flyctl (if not already installed)
brew install flyctl  # or: curl -L https://fly.io/install.sh | sh

# Sign up or log in
fly auth signup   # or: fly auth login

# Launch the HelloFly demo app
fly launch --image flyio/hellofly:latest
```

### Deploying This React App to Fly.io

1. **Create a Dockerfile in the `frontend` directory:**

```Dockerfile
# Dockerfile for Vite React app
FROM node:20-alpine AS build
WORKDIR /app
COPY ./frontend .
RUN npm install && npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

2. **Initialize Fly app and deploy:**
```bash
cd frontend
fly launch  # Accept defaults, or set a name/region
fly deploy
```

3. **Visit your deployed app:**
Fly will provide a URL like `https://<your-app-name>.fly.dev/` after deployment.

---

**Note:** If Fly.io cannot detect your framework, ensure you are in the `frontend` directory and have a `Dockerfile` present.

## Troubleshooting

- **No colors or gradients in the UI?**
  - Make sure you are using Tailwind CSS v3 (see compatibility note above).
  - Ensure your `postcss.config.cjs` uses the classic plugin syntax (see above).
  - Make sure your `src/index.css` contains only:
    ```css
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    ```
  - If you see a red background but no Tailwind styles, your CSS is loading but Tailwind is not being processed—check your PostCSS config and Tailwind version.
  - If you upgrade to Tailwind v4+, see the [Tailwind v4 migration guide](https://tailwindcss.com/docs/upgrade-guide) and update your PostCSS config accordingly.

## License
MIT
