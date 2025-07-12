from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import wandb
import weave
import os
from dotenv import load_dotenv
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

# Initialize Weights & Biases (W&B) project
WANDB_PROJECT = os.environ.get("WANDB_PROJECT", "weavehacks-demo")
wandb.init(project=WANDB_PROJECT)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/trace")
async def trace_event(request: Request):
    event = await request.json()
    # Log the event to W&B as a custom trace
    wandb.log({"trace_event": event})
    # Optionally, log to Weave (if using advanced tracing)
    # weave.log(event)
    return {"status": "logged", "event": event}

@app.post("/debug-wandb")
async def debug_wandb():
    # Log a test event to W&B
    wandb.log({"debug": "Frontend-Backend-W&B connection confirmed"})
    return {"status": "ok", "message": f"Connected to W&B project: {WANDB_PROJECT}"} 