from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# ── Observation ──────────────────────────────────────────────────
class LoopBreakerObservation(BaseModel):
    """What the agent sees at each step."""
    current_behavior_sequence: List[str]   # last N actions taken by the simulated user
    loop_detected: bool                     # whether a loop pattern was found
    loop_type: Optional[str]               # "search_repeat" | "content_revisit" | "app_switch" | None
    loop_depth: int                         # how many times the pattern repeated (0 if no loop)
    suggested_action: Optional[str]        # "decide" | "pause" | "reframe" | None
    step_number: int
    task_description: str
    time_elapsed: int                       # simulated seconds in session

# ── Action ───────────────────────────────────────────────────────
class LoopBreakerAction(BaseModel):
    """What the agent submits each step."""
    intervention: str   # "decide" | "pause" | "reframe" | "monitor" | "escalate"
    reason: Optional[str] = None            # agent's explanation (used in grading)
    confidence: float = 0.5                 # 0.0–1.0 confidence score

# ── Step Result ──────────────────────────────────────────────────
class StepResult(BaseModel):
    observation: LoopBreakerObservation
    reward: float                           # 0.0–1.0
    done: bool
    info: Dict[str, Any] = {}

# ── Reset Result ─────────────────────────────────────────────────
class ResetResult(BaseModel):
    observation: LoopBreakerObservation
    task_name: str

# ── State ────────────────────────────────────────────────────────
class EnvState(BaseModel):
    task_name: str
    step_count: int
    total_reward: float
    done: bool
    behavior_history: List[str]
