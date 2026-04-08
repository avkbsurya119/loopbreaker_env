"""LoopBreaker Environment - FastAPI Application

Exposes the LoopBreaker environment over HTTP/WebSocket.
"""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import from sibling modules (adjust path for installed package)
import sys
from pathlib import Path

# Add parent to path for local development
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from models import LoopBreakerAction, LoopBreakerObservation, LoopBreakerState, Event
from server.environment import LoopBreakerEnvironment
from server.tasks import SCENARIOS


# Create FastAPI app
app = FastAPI(
    title="LoopBreaker Environment",
    description="OpenEnv environment for detecting and interrupting decision loops",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active environments per session
environments: dict[str, LoopBreakerEnvironment] = {}


def get_or_create_env(session_id: str = "default") -> LoopBreakerEnvironment:
    """Get or create an environment for a session."""
    if session_id not in environments:
        environments[session_id] = LoopBreakerEnvironment()
    return environments[session_id]


# Request/Response models
class ResetRequest(BaseModel):
    """Request body for reset endpoint."""
    seed: int | None = None
    episode_id: str | None = None
    task_id: str | None = None
    session_id: str = "default"


class StepRequest(BaseModel):
    """Request body for step endpoint."""
    action: LoopBreakerAction
    session_id: str = "default"


class StateRequest(BaseModel):
    """Request body for state endpoint."""
    session_id: str = "default"


# Health endpoint
@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Environment endpoints
@app.post("/reset", response_model=LoopBreakerObservation)
async def reset(request: ResetRequest) -> LoopBreakerObservation:
    """Reset the environment and start a new episode."""
    env = get_or_create_env(request.session_id)
    try:
        observation = env.reset(
            seed=request.seed,
            episode_id=request.episode_id,
            task_id=request.task_id,
        )
        return observation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step", response_model=LoopBreakerObservation)
async def step(request: StepRequest) -> LoopBreakerObservation:
    """Execute an action and return the resulting observation."""
    env = get_or_create_env(request.session_id)
    try:
        observation = env.step(request.action)
        return observation
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state", response_model=LoopBreakerState)
async def state(session_id: str = "default") -> LoopBreakerState:
    """Get the current environment state."""
    env = get_or_create_env(session_id)
    return env.state


# Information endpoints
@app.get("/info")
async def info() -> dict[str, Any]:
    """Get information about the environment."""
    return {
        "name": "LoopBreaker",
        "version": "0.1.0",
        "description": "Environment for detecting overthinking and decision loops",
        "action_space": {
            "detection_actions": [
                "detect_repeated_search",
                "detect_revisit",
                "detect_app_switching",
                "continue_monitoring",
            ],
            "intervention_actions": [
                "pause",
                "decide",
                "reframe",
                "continue_monitoring",
            ],
        },
        "observation_space": {
            "recent_events": "List of user activity events",
            "task_id": "Current task identifier",
            "instructions": "Agent instructions",
            "done": "Episode completion flag",
            "reward": "Reward for last action",
            "step_count": "Current step number",
            "feedback": "Feedback about last action",
        },
        "reward_range": [-1.0, 2.5],
        "max_steps": 5,
    }


@app.get("/tasks")
async def list_tasks() -> list[dict[str, Any]]:
    """List all available tasks/scenarios."""
    return [
        {
            "task_id": s["task_id"],
            "description": s["description"],
            "difficulty": s["difficulty"],
            "category": s["category"],
        }
        for s in SCENARIOS
    ]


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> dict[str, Any]:
    """Get details of a specific task."""
    for scenario in SCENARIOS:
        if scenario["task_id"] == task_id:
            # Don't expose ground truth
            return {
                "task_id": scenario["task_id"],
                "description": scenario["description"],
                "difficulty": scenario["difficulty"],
                "category": scenario["category"],
                "num_events": len(scenario["events"]),
            }
    raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")


# Web UI endpoint (simple)
@app.get("/web")
async def web_ui():
    """Simple web interface."""
    return {
        "message": "LoopBreaker Environment",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "reset": "POST /reset",
            "step": "POST /step",
            "state": "GET /state",
            "tasks": "/tasks",
        },
        "docs": "/docs",
    }


def main():
    """Entry point for the server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
