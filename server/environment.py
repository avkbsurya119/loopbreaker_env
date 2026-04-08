"""LoopBreaker Environment - Main Environment Logic

Implements the Environment class for detecting and breaking decision loops.
"""

import random
import uuid
import sys
from pathlib import Path
from typing import Any

# Add parent to path for local development
_parent = Path(__file__).parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

try:
    from ..models import (
        Event,
        LoopBreakerAction,
        LoopBreakerObservation,
        LoopBreakerState,
    )
    from .grader import compute_reward, compute_episode_summary, is_valid_action
    from .tasks import SCENARIOS, get_scenario_by_id
except ImportError:
    from models import (
        Event,
        LoopBreakerAction,
        LoopBreakerObservation,
        LoopBreakerState,
    )
    from server.grader import compute_reward, compute_episode_summary, is_valid_action
    from server.tasks import SCENARIOS, get_scenario_by_id


class LoopBreakerEnvironment:
    """Environment for detecting overthinking and decision loops.

    This environment simulates user activity streams and challenges agents
    to identify loop patterns and recommend appropriate interventions.
    """

    SUPPORTS_CONCURRENT_SESSIONS = True
    MAX_STEPS = 5

    def __init__(self):
        """Initialize the environment."""
        self._state: LoopBreakerState | None = None
        self._detection_done: bool = False
        self._detection_correct: bool = False
        self._intervention_correct: bool = False

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        task_id: str | None = None,
        **kwargs: Any
    ) -> LoopBreakerObservation:
        """Reset the environment and start a new episode.

        Args:
            seed: Optional random seed for reproducibility
            episode_id: Optional episode identifier
            task_id: Optional specific task to use (otherwise random)
            **kwargs: Additional keyword arguments

        Returns:
            Initial observation for the episode
        """
        if seed is not None:
            random.seed(seed)

        # Select scenario
        if task_id:
            scenario = get_scenario_by_id(task_id)
            if scenario is None:
                scenario = random.choice(SCENARIOS)
        else:
            scenario = random.choice(SCENARIOS)

        # Create events from scenario
        events = [
            Event(type=e["type"], value=e["value"])
            for e in scenario["events"]
        ]

        # Initialize state
        self._state = LoopBreakerState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=scenario["task_id"],
            history=events,
            ground_truth_loop_type=scenario["correct_detection"],
            ground_truth_intervention=scenario["correct_intervention"],
            resolved=False,
            max_steps=self.MAX_STEPS,
            cumulative_reward=0.0,
        )

        self._detection_done = False
        self._detection_correct = False
        self._intervention_correct = False

        # Return initial observation
        return LoopBreakerObservation(
            recent_events=events,
            task_id=scenario["task_id"],
            instructions=self._get_instructions(scenario),
            done=False,
            reward=None,
            step_count=0,
            feedback=None,
            metadata={
                "difficulty": scenario["difficulty"],
                "category": scenario["category"],
                "description": scenario["description"],
            }
        )

    def step(
        self,
        action: LoopBreakerAction,
        timeout_s: float | None = None,
        **kwargs: Any
    ) -> LoopBreakerObservation:
        """Execute an action and return the resulting observation.

        Args:
            action: The action to execute
            timeout_s: Optional timeout in seconds
            **kwargs: Additional keyword arguments

        Returns:
            Observation after executing the action
        """
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        # Increment step count
        self._state.step_count += 1

        # Get current scenario
        scenario = get_scenario_by_id(self._state.task_id)
        if scenario is None:
            raise RuntimeError(f"Unknown task_id: {self._state.task_id}")

        # Validate action
        action_type = action.action_type
        if not is_valid_action(action_type):
            reward = -1.0
            feedback = f"Invalid action: {action_type}. Valid actions are: detect_repeated_search, detect_revisit, detect_app_switching, pause, decide, reframe, continue_monitoring"
            done = False
        else:
            # Compute reward
            reward, feedback, episode_done = compute_reward(
                action_type=action_type,
                scenario=scenario,
                step_count=self._state.step_count,
                detection_done=self._detection_done,
            )

            # Update detection state
            if not self._detection_done and action_type in {
                "detect_repeated_search", "detect_revisit",
                "detect_app_switching", "continue_monitoring"
            }:
                self._detection_done = True
                self._detection_correct = (action_type == scenario["correct_detection"])

            # Update intervention state
            if self._detection_done and action_type in {
                "pause", "decide", "reframe", "continue_monitoring"
            }:
                self._intervention_correct = (action_type == scenario["correct_intervention"])
                done = True
                self._state.resolved = self._detection_correct and self._intervention_correct
            else:
                done = episode_done

        # Update cumulative reward
        self._state.cumulative_reward += reward

        # Check max steps
        if self._state.step_count >= self._state.max_steps:
            done = True
            feedback += " (Max steps reached)"

        # Build observation
        metadata = {
            "difficulty": scenario["difficulty"],
            "category": scenario["category"],
            "detection_done": self._detection_done,
            "cumulative_reward": self._state.cumulative_reward,
        }

        if done:
            summary = compute_episode_summary(
                cumulative_reward=self._state.cumulative_reward,
                detection_correct=self._detection_correct,
                intervention_correct=self._intervention_correct,
                steps_taken=self._state.step_count,
            )
            metadata["episode_summary"] = summary

        return LoopBreakerObservation(
            recent_events=self._state.history,
            task_id=self._state.task_id,
            instructions=self._get_step_instructions(),
            done=done,
            reward=reward,
            step_count=self._state.step_count,
            feedback=feedback,
            metadata=metadata,
        )

    @property
    def state(self) -> LoopBreakerState:
        """Get the current environment state."""
        if self._state is None:
            return LoopBreakerState()
        return self._state

    def close(self) -> None:
        """Clean up environment resources."""
        self._state = None

    def _get_instructions(self, scenario: dict) -> str:
        """Get initial instructions for a scenario."""
        return (
            f"Task: {scenario['description']}\n\n"
            f"Analyze the user's recent activity pattern. Your goal is to:\n"
            f"1. Detect if there's a loop pattern (repeated_search, revisit, or app_switching)\n"
            f"2. If a loop is detected, recommend an intervention (pause, decide, or reframe)\n\n"
            f"If no loop pattern exists, use 'continue_monitoring'.\n\n"
            f"Difficulty: {scenario['difficulty']}"
        )

    def _get_step_instructions(self) -> str:
        """Get instructions for the current step."""
        if not self._detection_done:
            return (
                "First, classify the loop type. Use one of:\n"
                "- detect_repeated_search: User is searching for the same thing repeatedly\n"
                "- detect_revisit: User is revisiting the same content repeatedly\n"
                "- detect_app_switching: User is switching between apps indecisively\n"
                "- continue_monitoring: No clear loop pattern detected"
            )
        else:
            return (
                "Now recommend an intervention. Use one of:\n"
                "- pause: Suggest the user take a break\n"
                "- decide: Encourage the user to make a decision\n"
                "- reframe: Help the user reframe their approach\n"
                "- continue_monitoring: No intervention needed"
            )


# Singleton instance for the server
_environment_instance: LoopBreakerEnvironment | None = None


def get_environment() -> LoopBreakerEnvironment:
    """Get or create the environment singleton."""
    global _environment_instance
    if _environment_instance is None:
        _environment_instance = LoopBreakerEnvironment()
    return _environment_instance
