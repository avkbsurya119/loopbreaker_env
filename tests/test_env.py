"""Basic smoke tests for the LoopBreaker environment."""
import pytest
from server.env import LoopBreakerEnv
from server.models import LoopBreakerAction

def test_reset_easy():
    env = LoopBreakerEnv()
    result = env.reset("easy")
    assert result.task_name == "easy"
    assert result.observation.step_number == 0
    assert len(result.observation.current_behavior_sequence) >= 1

def test_step_returns_valid_reward():
    env = LoopBreakerEnv()
    env.reset("easy")
    action = LoopBreakerAction(intervention="decide", confidence=0.9)
    result = env.step(action)
    assert 0.0 <= result.reward <= 1.0
    assert isinstance(result.done, bool)

def test_state():
    env = LoopBreakerEnv()
    env.reset("medium")
    state = env.state()
    assert state.task_name == "medium"
    assert state.step_count == 0

def test_all_tasks():
    env = LoopBreakerEnv()
    for task in ["easy", "medium", "hard"]:
        result = env.reset(task)
        assert result.task_name == task
        action = LoopBreakerAction(intervention="monitor", confidence=0.5)
        step_result = env.step(action)
        assert 0.0 <= step_result.reward <= 1.0

def test_graders_output_valid_range():
    from server.graders import easy_grader, medium_grader, hard_grader
    dummy = [{"reward": 0.8, "loop_detected": True, "intervention": "decide", "confidence": 0.9}]
    for grader in [easy_grader, medium_grader, hard_grader]:
        score = grader.grade(dummy)
        assert 0.0 <= score <= 1.0
