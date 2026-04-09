"""
MEDIUM TASK: Detect a 3-step mixed loop (revisiting content + app switching).
Agent must choose between 'pause' and 'reframe' — requires pattern analysis.
Max 8 steps.
"""
import random

TASK_DESCRIPTION = (
    "A user is switching between apps and revisiting the same content indecisively. "
    "Detect the loop type and select the correct intervention: 'pause' or 'reframe'."
)

MEDIUM_SEQUENCES = [
    {
        "sequence": ["open:twitter", "open:instagram", "open:twitter", "open:instagram", "open:twitter"],
        "loop_type": "app_switch",
        "correct_intervention": "pause",
    },
    {
        "sequence": ["read:article_A", "read:article_B", "read:article_A", "read:article_B"],
        "loop_type": "content_revisit",
        "correct_intervention": "reframe",
    },
]

def get_sequence():
    return random.choice(MEDIUM_SEQUENCES)
