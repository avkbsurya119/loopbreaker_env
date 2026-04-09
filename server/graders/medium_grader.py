"""
Medium grader: scores both correctness AND efficiency (fewer steps = bonus).
"""

def grade(step_results: list) -> float:
    if not step_results:
        return 0.0
    best_reward = max(r.get("reward", 0.0) for r in step_results)
    steps_used = len(step_results)
    # Efficiency bonus: solving in ≤4 steps gives up to 0.1 bonus
    efficiency_bonus = max(0.0, (4 - steps_used) * 0.025) if best_reward >= 0.6 else 0.0
    score = min(best_reward + efficiency_bonus, 1.0)
    return round(score, 4)
