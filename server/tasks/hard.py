"""
HARD TASK: Detect a compound loop (all three: search_repeat + content_revisit + app_switch)
in a noisy 10+ step sequence. Agent must correctly identify ALL loop types AND the optimal
intervention, AND provide a confidence >= 0.8.
Genuinely challenges frontier models.
"""
import random

TASK_DESCRIPTION = (
    "A user is exhibiting a complex multi-modal decision loop across search, content, and apps. "
    "You must identify ALL active loop types, select the single best intervention, "
    "and express confidence >= 0.8 to receive full credit."
)

HARD_SEQUENCES = [
    ["search:buy car", "open:autotrader", "search:buy car", "read:review_A",
     "open:edmunds", "read:review_A", "search:buy car", "open:autotrader",
     "open:edmunds", "read:review_A", "search:buy car"],
    ["search:move city", "open:zillow", "read:listing_1", "search:move city",
     "open:apartments", "read:listing_1", "open:zillow", "search:move city",
     "read:listing_1", "open:apartments", "search:move city"],
]

ALL_LOOP_TYPES = ["search_repeat", "content_revisit", "app_switch"]

def get_sequence():
    return random.choice(HARD_SEQUENCES)
