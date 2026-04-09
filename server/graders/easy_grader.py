"""
Easy grader: deterministic, reproducible.
Scores the agent's BEST step result across the episode.
"""

def grade(step_results: list) -> float:
    """
    Args:
        step_results: list of dicts with keys: intervention, reward, loop_detected
    Returns:
        float in [0.0, 1.0]
    """
    if not step_results:
        return 0.0
    best_reward = max(r.get("reward", 0.0) for r in step_results)
    return round(min(max(best_reward, 0.0), 1.0), 4)
