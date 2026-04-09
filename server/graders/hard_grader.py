"""
Hard grader: compound scoring.
- Correct loop type detection: 0.3
- Correct intervention: 0.4
- Confidence >= 0.8: 0.3
All criteria must be partially met; partial credit awarded.
"""

def grade(step_results: list) -> float:
    if not step_results:
        return 0.0

    best = max(step_results, key=lambda r: r.get("reward", 0.0))
    base_reward = best.get("reward", 0.0)

    # Compound check
    loop_score = 0.3 if best.get("loop_detected", False) else 0.0
    intervention_score = 0.4 if best.get("intervention") in ["reframe", "escalate"] else 0.0
    confidence_score = 0.3 if best.get("confidence", 0.0) >= 0.8 else best.get("confidence", 0.0) * 0.3

    compound = loop_score + intervention_score + confidence_score
    final = max(base_reward, compound)  # take the higher of the two
    return round(min(max(final, 0.0), 1.0), 4)
