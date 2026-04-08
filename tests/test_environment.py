"""Tests for the LoopBreaker Environment."""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from models import LoopBreakerAction, LoopBreakerObservation, LoopBreakerState
from server.environment import LoopBreakerEnvironment
from server.grader import (
    grade_detection,
    grade_intervention,
    compute_reward,
    is_valid_action,
)
from server.tasks import SCENARIOS, get_scenario_by_id


class TestEnvironmentReset:
    """Test environment reset functionality."""

    def test_reset_returns_observation(self):
        """Reset should return a valid observation."""
        env = LoopBreakerEnvironment()
        obs = env.reset()

        assert isinstance(obs, LoopBreakerObservation)
        assert obs.done is False
        assert obs.step_count == 0
        assert obs.reward is None
        assert len(obs.recent_events) > 0

    def test_reset_with_seed_is_reproducible(self):
        """Reset with same seed should produce same scenario."""
        env1 = LoopBreakerEnvironment()
        env2 = LoopBreakerEnvironment()

        obs1 = env1.reset(seed=42)
        obs2 = env2.reset(seed=42)

        assert obs1.task_id == obs2.task_id

    def test_reset_with_task_id(self):
        """Reset with specific task_id should use that task."""
        env = LoopBreakerEnvironment()
        obs = env.reset(task_id="repeated_search_easy_1")

        assert obs.task_id == "repeated_search_easy_1"

    def test_reset_initializes_state(self):
        """Reset should initialize state correctly."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        state = env.state
        assert state.step_count == 0
        assert state.task_id == "repeated_search_easy_1"
        assert state.cumulative_reward == 0.0


class TestEnvironmentStep:
    """Test environment step functionality."""

    def test_step_increments_count(self):
        """Step should increment step count."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        action = LoopBreakerAction(action_type="detect_repeated_search")
        obs = env.step(action)

        assert obs.step_count == 1
        assert env.state.step_count == 1

    def test_step_returns_reward(self):
        """Step should return a reward."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        action = LoopBreakerAction(action_type="detect_repeated_search")
        obs = env.step(action)

        assert obs.reward is not None

    def test_correct_detection_positive_reward(self):
        """Correct detection should give positive reward."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        action = LoopBreakerAction(action_type="detect_repeated_search")
        obs = env.step(action)

        assert obs.reward > 0

    def test_wrong_detection_negative_reward(self):
        """Wrong detection should give negative reward."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        # Wrong detection type
        action = LoopBreakerAction(action_type="detect_app_switching")
        obs = env.step(action)

        assert obs.reward < 0

    def test_invalid_action_negative_reward(self):
        """Invalid action should give negative reward."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        action = LoopBreakerAction(action_type="invalid_action")
        obs = env.step(action)

        assert obs.reward == -1.0

    def test_episode_ends_after_intervention(self):
        """Episode should end after detection + intervention."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        # Detection
        obs = env.step(LoopBreakerAction(action_type="detect_repeated_search"))
        assert obs.done is False

        # Intervention
        obs = env.step(LoopBreakerAction(action_type="decide"))
        assert obs.done is True

    def test_episode_ends_at_max_steps(self):
        """Episode should end at max steps."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        # Take max steps with continue_monitoring
        for i in range(env.MAX_STEPS):
            action = LoopBreakerAction(action_type="continue_monitoring")
            obs = env.step(action)

        assert obs.done is True


class TestGrader:
    """Test grading functions."""

    def test_valid_actions(self):
        """Test action validation."""
        assert is_valid_action("detect_repeated_search")
        assert is_valid_action("pause")
        assert is_valid_action("decide")
        assert not is_valid_action("invalid")

    def test_grade_detection_correct(self):
        """Correct detection should return positive grade."""
        scenario = get_scenario_by_id("repeated_search_easy_1")
        is_correct, reward, _ = grade_detection("detect_repeated_search", scenario)

        assert is_correct is True
        assert reward > 0

    def test_grade_detection_wrong(self):
        """Wrong detection should return negative grade."""
        scenario = get_scenario_by_id("repeated_search_easy_1")
        is_correct, reward, _ = grade_detection("detect_app_switching", scenario)

        assert is_correct is False
        assert reward < 0

    def test_grade_intervention_correct(self):
        """Correct intervention should return positive grade."""
        scenario = get_scenario_by_id("repeated_search_easy_1")
        is_correct, reward, _ = grade_intervention("decide", scenario)

        assert is_correct is True
        assert reward > 0

    def test_early_detection_bonus(self):
        """Early detection should get bonus reward."""
        scenario = get_scenario_by_id("repeated_search_easy_1")

        # Step 1 - early bonus
        reward_step1, _, _ = compute_reward(
            "detect_repeated_search", scenario, step_count=1
        )

        # Step 3 - no early bonus
        reward_step3, _, _ = compute_reward(
            "detect_repeated_search", scenario, step_count=3
        )

        assert reward_step1 > reward_step3


class TestScenarios:
    """Test scenario definitions."""

    def test_scenarios_exist(self):
        """Should have multiple scenarios."""
        assert len(SCENARIOS) >= 10

    def test_scenarios_have_required_fields(self):
        """All scenarios should have required fields."""
        required_fields = [
            "task_id",
            "description",
            "difficulty",
            "category",
            "events",
            "correct_detection",
            "correct_intervention",
        ]

        for scenario in SCENARIOS:
            for field in required_fields:
                assert field in scenario, f"Missing {field} in {scenario['task_id']}"

    def test_scenario_categories(self):
        """Should have scenarios for all categories."""
        categories = {s["category"] for s in SCENARIOS}

        assert "repeated_search" in categories
        assert "revisit" in categories
        assert "app_switching" in categories
        assert "no_loop" in categories

    def test_scenario_difficulties(self):
        """Should have scenarios for all difficulty levels."""
        difficulties = {s["difficulty"] for s in SCENARIOS}

        assert "easy" in difficulties
        assert "medium" in difficulties
        assert "hard" in difficulties


class TestFullEpisode:
    """Test complete episode flows."""

    def test_perfect_episode(self):
        """Test a perfect episode with correct actions."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="repeated_search_easy_1")

        # Correct detection
        obs = env.step(LoopBreakerAction(action_type="detect_repeated_search"))
        assert obs.reward > 0

        # Correct intervention
        obs = env.step(LoopBreakerAction(action_type="decide"))
        assert obs.reward > 0
        assert obs.done is True

        # Check cumulative reward is positive
        assert env.state.cumulative_reward > 0

    def test_no_loop_episode(self):
        """Test episode with no loop scenario."""
        env = LoopBreakerEnvironment()
        env.reset(task_id="no_loop_1")

        # Correct: no detection needed
        obs = env.step(LoopBreakerAction(action_type="continue_monitoring"))
        assert obs.reward >= 0

        # Correct: no intervention needed
        obs = env.step(LoopBreakerAction(action_type="continue_monitoring"))
        assert obs.done is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
