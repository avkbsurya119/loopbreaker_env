"""
EASY TASK: Detect a simple 2-step repeated search loop.
The simulated user searches the same query twice. Agent must intervene with 'decide'.
Max 5 steps. Clear, deterministic success criteria.
"""
import random

TASK_DESCRIPTION = (
    "A user is repeatedly searching the same query. "
    "Detect the loop and choose the correct intervention: 'decide'."
)

# Pre-scripted behavior sequences that always produce a loop
EASY_SEQUENCES = [
    ["search:laptop deals", "browse:results", "search:laptop deals", "browse:results"],
    ["search:weather today", "browse:weather", "search:weather today", "browse:weather"],
    ["search:best coffee", "browse:results", "search:best coffee", "browse:results"],
]

def get_sequence():
    return random.choice(EASY_SEQUENCES)

def get_correct_intervention(loop_type: str) -> str:
    return "decide"   # easy task always expects "decide"
