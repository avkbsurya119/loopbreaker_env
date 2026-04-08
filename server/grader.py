"""LoopBreaker Environment - Grading Logic

Contains functions for evaluating agent actions and computing rewards.
"""

# Detection action types
DETECTION_ACTIONS = {
    "detect_repeated_search",
    "detect_revisit",
    "detect_app_switching",
    "continue_monitoring",
}

# Intervention action types
INTERVENTION_ACTIONS = {
    "pause",
    "decide",
    "reframe",
    "continue_monitoring",
}

# All valid actions
ALL_ACTIONS = DETECTION_ACTIONS | INTERVENTION_ACTIONS


def is_valid_action(action_type: str) -> bool:
    """Check if an action type is valid."""
    return action_type in ALL_ACTIONS


def is_detection_action(action_type: str) -> bool:
    """Check if an action is a detection action."""
    return action_type in DETECTION_ACTIONS


def is_intervention_action(action_type: str) -> bool:
    """Check if an action is an intervention action."""
    return action_type in INTERVENTION_ACTIONS


def grade_detection(action_type: str, scenario: dict) -> tuple[bool, float, str]:
    """Grade a detection action.

    Args:
        action_type: The action taken by the agent
        scenario: The current scenario dictionary

    Returns:
        Tuple of (is_correct, reward, feedback_message)
    """
    correct_detection = scenario.get("correct_detection", "")

    if action_type == correct_detection:
        if scenario.get("category") == "no_loop":
            return True, 0.5, "Correct: No loop pattern detected."
        return True, 1.0, f"Correct detection: {action_type}"

    # Wrong detection
    if action_type == "continue_monitoring" and scenario.get("category") != "no_loop":
        return False, -0.25, "Missed loop pattern. Should have detected a loop."

    if scenario.get("category") == "no_loop" and action_type != "continue_monitoring":
        return False, -0.5, f"False positive: Detected {action_type} but no loop exists."

    return False, -0.5, f"Wrong detection: {action_type}. Expected: {correct_detection}"


def grade_intervention(action_type: str, scenario: dict) -> tuple[bool, float, str]:
    """Grade an intervention action.

    Args:
        action_type: The action taken by the agent
        scenario: The current scenario dictionary

    Returns:
        Tuple of (is_correct, reward, feedback_message)
    """
    correct_intervention = scenario.get("correct_intervention", "")

    if action_type == correct_intervention:
        if scenario.get("category") == "no_loop":
            return True, 0.5, "Correct: Continued monitoring (no intervention needed)."
        return True, 1.0, f"Correct intervention: {action_type}"

    # Partially correct interventions (still helpful but not optimal)
    if scenario.get("category") != "no_loop" and action_type in INTERVENTION_ACTIONS:
        if action_type == "continue_monitoring":
            return False, -0.25, "Should have recommended an intervention."
        # Different intervention, but still an intervention
        return False, 0.25, f"Acceptable intervention: {action_type}, but {correct_intervention} would be better."

    return False, -0.5, f"Wrong intervention: {action_type}. Expected: {correct_intervention}"


def compute_reward(
    action_type: str,
    scenario: dict,
    step_count: int,
    detection_done: bool = False
) -> tuple[float, str, bool]:
    """Compute the total reward for an action.

    Args:
        action_type: The action taken by the agent
        scenario: The current scenario dictionary
        step_count: Current step number (1-indexed)
        detection_done: Whether detection phase is complete

    Returns:
        Tuple of (reward, feedback_message, is_episode_done)
    """
    if not is_valid_action(action_type):
        return -1.0, f"Invalid action: {action_type}", False

    # Early detection bonus
    early_bonus = 0.0
    if step_count == 1:
        early_bonus = 0.5
    elif step_count == 2:
        early_bonus = 0.25

    if not detection_done:
        # In detection phase
        if is_detection_action(action_type):
            is_correct, base_reward, feedback = grade_detection(action_type, scenario)
            if is_correct:
                total_reward = base_reward + early_bonus
                if early_bonus > 0:
                    feedback += f" (Early detection bonus: +{early_bonus})"
                return total_reward, feedback, False  # Move to intervention phase
            return base_reward, feedback, False
        else:
            # Skipped detection, went straight to intervention
            return -0.25, "Should classify the loop type before recommending intervention.", False
    else:
        # In intervention phase
        if is_intervention_action(action_type):
            is_correct, base_reward, feedback = grade_intervention(action_type, scenario)
            return base_reward, feedback, True  # Episode done after intervention
        else:
            return -0.25, "Should recommend an intervention (pause, decide, or reframe).", False


def compute_episode_summary(
    cumulative_reward: float,
    detection_correct: bool,
    intervention_correct: bool,
    steps_taken: int
) -> dict:
    """Compute summary statistics for a completed episode.

    Args:
        cumulative_reward: Total reward accumulated
        detection_correct: Whether detection was correct
        intervention_correct: Whether intervention was correct
        steps_taken: Number of steps taken

    Returns:
        Dictionary with summary statistics
    """
    # Efficiency score (fewer steps = better)
    efficiency = max(0.0, 1.0 - (steps_taken - 2) * 0.1)

    # Overall performance
    if detection_correct and intervention_correct:
        performance = "excellent"
    elif detection_correct or intervention_correct:
        performance = "partial"
    else:
        performance = "poor"

    return {
        "cumulative_reward": cumulative_reward,
        "detection_correct": detection_correct,
        "intervention_correct": intervention_correct,
        "steps_taken": steps_taken,
        "efficiency_score": efficiency,
        "performance": performance,
    }
