"""Local test script for the LoopBreaker environment.

Run this script to test the environment locally without starting the server.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import LoopBreakerAction
from server.environment import LoopBreakerEnvironment


def main():
    """Run a simple test of the environment."""
    print("=" * 60)
    print("LoopBreaker Environment - Local Test")
    print("=" * 60)

    env = LoopBreakerEnvironment()

    # Test 1: Repeated search scenario
    print("\n--- Test 1: Repeated Search (Easy) ---")
    obs = env.reset(task_id="repeated_search_easy_1")
    print(f"Task: {obs.task_id}")
    print(f"Events: {[(e.type, e.value) for e in obs.recent_events]}")
    print(f"Instructions: {obs.instructions[:100]}...")

    # Correct detection
    action = LoopBreakerAction(action_type="detect_repeated_search")
    obs = env.step(action)
    print(f"\nAction: detect_repeated_search")
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")

    # Correct intervention
    action = LoopBreakerAction(action_type="decide")
    obs = env.step(action)
    print(f"\nAction: decide")
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")
    print(f"Done: {obs.done}")
    print(f"Cumulative Reward: {env.state.cumulative_reward}")

    # Test 2: App switching scenario
    print("\n--- Test 2: App Switching (Easy) ---")
    obs = env.reset(task_id="app_switch_easy_1")
    print(f"Task: {obs.task_id}")
    print(f"Events: {[(e.type, e.value) for e in obs.recent_events]}")

    # Correct detection
    obs = env.step(LoopBreakerAction(action_type="detect_app_switching"))
    print(f"\nAction: detect_app_switching")
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")

    # Correct intervention
    obs = env.step(LoopBreakerAction(action_type="pause"))
    print(f"\nAction: pause")
    print(f"Reward: {obs.reward}, Done: {obs.done}")

    # Test 3: Wrong detection
    print("\n--- Test 3: Wrong Detection ---")
    obs = env.reset(task_id="revisit_easy_1")
    print(f"Task: {obs.task_id} (Should detect: revisit)")

    # Wrong detection
    obs = env.step(LoopBreakerAction(action_type="detect_repeated_search"))
    print(f"\nAction: detect_repeated_search (WRONG)")
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")

    # Test 4: No loop scenario
    print("\n--- Test 4: No Loop (False Positive Test) ---")
    obs = env.reset(task_id="no_loop_1")
    print(f"Task: {obs.task_id}")
    print(f"Events: {[(e.type, e.value) for e in obs.recent_events]}")

    # Correct: continue monitoring
    obs = env.step(LoopBreakerAction(action_type="continue_monitoring"))
    print(f"\nAction: continue_monitoring")
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")

    # Test 5: Invalid action
    print("\n--- Test 5: Invalid Action ---")
    obs = env.reset(task_id="repeated_search_easy_1")
    obs = env.step(LoopBreakerAction(action_type="invalid_action"))
    print(f"Action: invalid_action")
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")

    print("\n" + "=" * 60)
    print("All local tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
