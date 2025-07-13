from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import wandb
import weave
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from crew_runner import run_crew
load_dotenv()

app = FastAPI()

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store W&B status
wandb_initialized = False
WANDB_PROJECT = os.environ.get("WANDB_PROJECT", "weavehacks")

def initialize_wandb():
    """Initialize W&B with error handling"""
    global wandb_initialized
    try:
        wandb.init(project=WANDB_PROJECT)
        print(f"✅ W&B initialized successfully with project: {WANDB_PROJECT}")
        wandb_initialized = True
    except Exception as e:
        print(f"⚠️ W&B initialization failed: {e}")
        print("⚠️ App will continue without W&B logging")
        wandb_initialized = False

@app.on_event("startup")
async def startup_event():
    """Initialize W&B when the app starts"""
    initialize_wandb()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/trace")
async def trace_event(request: Request):
    event = await request.json()
    # Log the event to W&B as a custom trace (if available)
    if wandb_initialized:
        try:
            wandb.log({"trace_event": event})
        except Exception as e:
            print(f"⚠️ Failed to log to W&B: {e}")
    else:
        print(f"📝 Trace event (W&B not available): {event}")
    # Optionally, log to Weave (if using advanced tracing)
    # weave.log(event)
    return {"status": "logged", "event": event}

@app.post("/debug-wandb")
async def debug_wandb():
    if wandb_initialized:
        try:
            # Log a test event to W&B
            wandb.log({"debug": "Frontend-Backend-W&B connection confirmed"})
            return {"status": "ok", "message": f"Connected to W&B project: {WANDB_PROJECT}"}
        except Exception as e:
            return {"status": "error", "message": f"W&B logging failed: {e}"}
    else:
        return {"status": "warning", "message": "W&B not available - app running without W&B integration"}

class CrewRequest(BaseModel):
    topic: str

@app.post("/run-crew")
async def run_crew_endpoint(req: CrewRequest):
    result = run_crew(req.topic)
    return {"result": result}
