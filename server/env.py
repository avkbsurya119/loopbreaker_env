import random
from typing import Optional
from server.models import (
    LoopBreakerObservation, LoopBreakerAction,
    StepResult, ResetResult, EnvState
)
from server.tasks import easy, medium, hard

TASK_MAP = {"easy": easy, "medium": medium, "hard": hard}

def detect_loop(sequence: list):
    """Detect repeat patterns in behavior sequence. Returns (loop_detected, loop_type, depth)."""
    if len(sequence) < 2:
        return False, None, 0

    # Check for search repeats
    searches = [s for s in sequence if s.startswith("search:")]
    if len(searches) >= 2 and len(set(searches)) < len(searches):
        return True, "search_repeat", searches.count(max(set(searches), key=searches.count))

    # Check for content revisit
    reads = [s for s in sequence if s.startswith("read:")]
    if len(reads) >= 2 and len(set(reads)) < len(reads):
        return True, "content_revisit", reads.count(max(set(reads), key=reads.count))

    # Check for app switching
    apps = [s for s in sequence if s.startswith("open:")]
    if len(apps) >= 4:
        pairs = [(apps[i], apps[i+1]) for i in range(len(apps)-1)]
        for pair in pairs:
            if pairs.count(pair) >= 2:
                return True, "app_switch", pairs.count(pair)

    return False, None, 0


class LoopBreakerEnv:
    def __init__(self):
        self.task_name: str = "easy"
        self.step_count: int = 0
        self.total_reward: float = 0.0
        self.done: bool = False
        self.behavior_history: list = []
        self._task_module = None
        self._task_data = None
        self._full_sequence: list = []
        self._max_steps: int = 5
        self._time_elapsed: int = 0

    def reset(self, task_name: str = "easy") -> ResetResult:
        self.task_name = task_name
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        self.behavior_history = []
        self._time_elapsed = 0

        self._task_module = TASK_MAP[task_name]
        if task_name == "easy":
            self._full_sequence = self._task_module.get_sequence()
            self._max_steps = 5
        elif task_name == "medium":
            self._task_data = self._task_module.get_sequence()
            self._full_sequence = self._task_data["sequence"]
            self._max_steps = 8
        else:
            self._full_sequence = self._task_module.get_sequence()
            self._max_steps = 12

        # Show first 2 actions in initial observation
        initial_slice = self._full_sequence[:2]
        loop_detected, loop_type, loop_depth = detect_loop(initial_slice)

        obs = LoopBreakerObservation(
            current_behavior_sequence=initial_slice,
            loop_detected=loop_detected,
            loop_type=loop_type,
            loop_depth=loop_depth,
            suggested_action=None,
            step_number=0,
            task_description=self._task_module.TASK_DESCRIPTION,
            time_elapsed=self._time_elapsed,
        )
        return ResetResult(observation=obs, task_name=task_name)

    def step(self, action: LoopBreakerAction) -> StepResult:
        if self.done:
            raise RuntimeError("Episode done — call reset() first.")

        self.step_count += 1
        self._time_elapsed += random.randint(10, 60)

        # Reveal more of the behavior sequence each step
        reveal_up_to = min(2 + self.step_count * 2, len(self._full_sequence))
        visible_sequence = self._full_sequence[:reveal_up_to]

        loop_detected, loop_type, loop_depth = detect_loop(visible_sequence)

        # ── Compute reward ────────────────────────────────────────
        reward = self._compute_reward(action, loop_detected, loop_type, loop_depth)
        self.total_reward += reward

        done = (self.step_count >= self._max_steps) or (reward >= 0.9)
        self.done = done

        obs = LoopBreakerObservation(
            current_behavior_sequence=visible_sequence,
            loop_detected=loop_detected,
            loop_type=loop_type,
            loop_depth=loop_depth,
            suggested_action=action.intervention,
            step_number=self.step_count,
            task_description=self._task_module.TASK_DESCRIPTION,
            time_elapsed=self._time_elapsed,
        )

        return StepResult(
            observation=obs,
            reward=round(reward, 4),
            done=done,
            info={"step": self.step_count, "total_reward": round(self.total_reward, 4)},
        )

    def _compute_reward(self, action: LoopBreakerAction, loop_detected: bool,
                        loop_type: Optional[str], loop_depth: int) -> float:
        """
        Meaningful reward with partial signals — not just binary end-of-episode.
        Penalizes wrong interventions and inaction on detected loops.
        """
        base = 0.0

        if self.task_name == "easy":
            correct = "decide"
            if loop_detected and action.intervention == correct:
                base = 0.8 + min(action.confidence, 1.0) * 0.2
            elif loop_detected and action.intervention == "monitor":
                base = 0.2   # partial credit for observing
            elif not loop_detected:
                base = 0.1   # too early, but no penalty
            else:
                base = 0.0   # wrong intervention

        elif self.task_name == "medium":
            correct = self._task_data.get("correct_intervention", "pause")
            if loop_detected and action.intervention == correct:
                base = 0.7 + min(action.confidence, 1.0) * 0.3
            elif loop_detected and action.intervention in ["decide", "pause", "reframe"]:
                base = 0.3   # right category, wrong choice
            elif action.intervention == "monitor":
                base = 0.15
            else:
                base = 0.0

        elif self.task_name == "hard":
            # Hard: must identify loop + correct intervention + high confidence
            if loop_detected and action.intervention in ["reframe", "escalate"]:
                confidence_bonus = max(0.0, action.confidence - 0.8) * 1.0  # only above 0.8
                base = 0.6 + confidence_bonus * 0.4
            elif loop_detected:
                base = 0.3
            else:
                base = 0.05  # tiny partial credit for monitoring

        # Penalize infinite-loop / destructive actions (per spec)
        if action.intervention == "loop" or action.confidence < 0.0 or action.confidence > 1.0:
            base = max(0.0, base - 0.5)

        return round(min(max(base, 0.0), 1.0), 4)

    def state(self) -> EnvState:
        return EnvState(
            task_name=self.task_name,
            step_count=self.step_count,
            total_reward=self.total_reward,
            done=self.done,
            behavior_history=self._full_sequence[:2 + self.step_count * 2],
        )
