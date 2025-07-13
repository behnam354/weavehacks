# WeaveHacks System Architecture

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        WeaveHacks System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                    ┌─────────────────┐     │
│  │   Frontend      │                    │    Backend      │     │
│  │   (React)       │◄──────────────────►│   (FastAPI)     │     │
│  │                 │                    │                 │     │
│  │ • QR Generator  │                    │ • Crew AI       │     │
│  │ • Agent Monitor │                    │ • W&B Integration│     │
│  │ • Results View  │                    │ • Weave Tracing │     │
│  │ • Live Logs     │                    │ • API Endpoints │     │
│  └─────────────────┘                    └─────────────────┘     │
│           │                                    │                │
│           │                                    │                │
│  ┌─────────────────┐                    ┌─────────────────┐     │
│  │   Fly.io        │                    │   External      │     │
│  │   Frontend      │                    │   Services      │     │
│  │   (Nginx)       │                    │                 │     │
│  └─────────────────┘                    │ • W&B API       │     │
│                                         │ • Weave API      │     │
│                                         │ • Crew AI Lib    │     │
│                                         └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

```
User Input
    │
    ▼
┌─────────────┐    HTTP Request    ┌─────────────┐
│  Frontend   │ ──────────────────► │   Backend   │
│  (React)    │                    │  (FastAPI)  │
└─────────────┘                    └─────────────┘
    │                                    │
    │                                    ▼
    │                            ┌─────────────┐
    │                            │  Crew AI    │
    │                            │ Orchestrator│
    │                            └─────────────┘
    │                                    │
    │                                    ▼
    │                            ┌─────────────┐
    │                            │ W&B LLM     │
    │                            │ (Agents)    │
    │                            └─────────────┘
    │                                    │
    │                                    ▼
    │                            ┌─────────────┐
    │                            │ Weave       │
    │                            │ (Tracing)   │
    │                            └─────────────┘
    │                                    │
    ▼                                    ▼
┌─────────────┐    HTTP Response   ┌─────────────┐
│  Frontend   │ ◄───────────────── │   Backend   │
│  (Display)  │                    │  (Result)   │
└─────────────┘                    └─────────────┘
```

## 🎯 Component Architecture

### Frontend Components
```
App.jsx
└── ArtisticQRGenerator
    ├── Control Panel
    │   ├── QR Data Input
    │   ├── Art Style Selector
    │   └── Crew AI Topic Input
    ├── Agent Monitor
    │   ├── Active Agents Status
    │   └── Agent Configuration
    ├── Live Logs
    │   ├── Agent Activity Logs
    │   └── Protocol Messages
    └── Results Display
        ├── Generated QR Code
        ├── Crew AI Results
        └── Weave Trace Data
```

### Backend Services
```
FastAPI Application
├── API Endpoints
│   ├── /health (Health Check)
│   ├── /trace (Event Logging)
│   ├── /debug-wandb (W&B Test)
│   └── /run-crew (Crew AI Workflow)
├── Core Services
│   ├── Crew AI Runner
│   ├── Weave Initialization
│   └── W&B Integration
└── Agent Orchestration
    ├── Research Analyst Agent
    ├── Report Writer Agent
    └── Custom W&B LLM
```

## 🚀 Deployment Architecture

### Fly.io Infrastructure
```
┌─────────────────────────────────────────────────────────────┐
│                    Fly.io Platform                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐              ┌─────────────────┐      │
│  │  Frontend App   │              │  Backend App    │      │
│  │                 │              │                 │      │
│  │ • Nginx Server  │              │ • Python 3.11   │      │
│  │ • React Build   │              │ • FastAPI       │      │
│  │ • Static Files  │              │ • Docker        │      │
│  │ • HTTPS/SSL     │              │ • Health Checks │      │
│  └─────────────────┘              └─────────────────┘      │
│           │                              │                 │
│           │                              │                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              External Services                      │   │
│  │                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   W&B API   │  │  Weave API  │  │ Crew AI Lib │ │   │
│  │  │             │  │             │  │             │ │   │
│  │  │ • LLM Calls │  │ • Tracing   │  │ • Agents    │ │   │
│  │  │ • Logging   │  │ • Monitoring│  │ • Workflows │ │   │
│  │  │ • Projects  │  │ • Analytics │  │ • Tasks     │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

### Frontend
- **React 19.1.0** - UI Framework
- **Vite 7.0.4** - Build Tool
- **Tailwind CSS 3.4.3** - Styling
- **Lucide React 0.525.0** - Icons
- **Nginx** - Web Server (Production)

### Backend
- **FastAPI** - API Framework
- **Python 3.11** - Runtime
- **Crew AI** - Agent Orchestration
- **Weave** - Distributed Tracing
- **Weights & Biases** - ML Monitoring
- **Docker** - Containerization

### External Services
- **W&B Inference API** - LLM Services
- **Weave API** - Tracing & Analytics
- **Fly.io** - Cloud Deployment

## 🔄 Agent Workflow

```
Crew AI Workflow
    │
    ▼
┌─────────────┐
│ Research    │ ──► Market Analysis
│ Analyst     │ ──► Key Players
│ Agent       │ ──► Growth Trends
└─────────────┘
    │
    ▼
┌─────────────┐
│ Report      │ ──► Structure Report
│ Writer      │ ──► Format Findings
│ Agent       │ ──► Generate Conclusions
└─────────────┘
    │
    ▼
┌─────────────┐
│ Investment  │
│ Report      │
└─────────────┘
```

## 📊 Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    Observability Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Weave     │  │     W&B     │  │   Fly.io    │         │
│  │             │  │             │  │             │         │
│  │ • Traces    │  │ • Logs      │  │ • Health    │         │
│  │ • Spans     │  │ • Metrics   │  │ • Monitoring│         │
│  │ • Analytics │  │ • Experiments│  │ • Alerts    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Security & Configuration

### Environment Variables
```
WANDB_API_KEY=your_wandb_api_key
WANDB_PROJECT=weavehacks
OPENAI_API_KEY=your_openai_key (optional)
```

### CORS Configuration
- Frontend: Development mode allows all origins
- Backend: Configured for cross-origin requests
- Production: Secure HTTPS communication

### Error Handling
- Graceful degradation when services unavailable
- Comprehensive error boundaries
- Structured error responses
- Health check endpoints

## 🚀 Performance Optimizations

### Frontend
- Vite for fast development and optimized builds
- Tailwind CSS for minimal CSS bundle
- React 19 with improved performance
- Nginx with gzip compression and caching

### Backend
- Python 3.11 for better performance
- FastAPI for async request handling
- Docker layer caching for faster deployments
- Health checks for reliability

## 🔮 Future Enhancements

### Planned Features
- Real QR code generation with artistic overlays
- Integration with Exa for web search
- BrowserBase automation for data collection
- Google Cloud AI for image generation
- Enhanced agent capabilities

### Scalability
- Horizontal scaling with Fly.io
- Database integration for persistent storage
- Caching layer for improved performance
- Microservices architecture evolution 