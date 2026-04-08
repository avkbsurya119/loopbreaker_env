"""LoopBreaker Environment Server

Server-side components for the LoopBreaker environment.
"""

import sys
from pathlib import Path

# Add parent to path for local development
_parent = Path(__file__).parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

try:
    from .environment import LoopBreakerEnvironment, get_environment
    from .grader import (
        compute_reward,
        compute_episode_summary,
        grade_detection,
        grade_intervention,
        is_valid_action,
    )
    from .tasks import SCENARIOS, get_scenario_by_id, get_scenarios_by_category, get_scenarios_by_difficulty
except ImportError:
    from server.environment import LoopBreakerEnvironment, get_environment
    from server.grader import (
        compute_reward,
        compute_episode_summary,
        grade_detection,
        grade_intervention,
        is_valid_action,
    )
    from server.tasks import SCENARIOS, get_scenario_by_id, get_scenarios_by_category, get_scenarios_by_difficulty

__all__ = [
    "LoopBreakerEnvironment",
    "get_environment",
    "compute_reward",
    "compute_episode_summary",
    "grade_detection",
    "grade_intervention",
    "is_valid_action",
    "SCENARIOS",
    "get_scenario_by_id",
    "get_scenarios_by_category",
    "get_scenarios_by_difficulty",
]
