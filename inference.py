"""
LoopBreaker Environment - Inference Script
============================================
Detects decision loops (repeated searches, revisits, app switching) and recommends interventions.
"""

import os
import textwrap
from typing import List, Optional

import httpx
from openai import OpenAI

# Environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# LoopBreaker env config
ENV_URL = os.getenv("LOOPBREAKER_URL", "https://avkbsurya119-loopbreaker-env.hf.space")
TASK_NAME = os.getenv("LOOPBREAKER_TASK", "loopbreaker")
BENCHMARK = "loopbreaker_env"
MAX_STEPS = 5
MAX_TOTAL_REWARD = 2.5  # Max possible: 1.0 detection + 0.5 early bonus + 1.0 intervention

SYSTEM_PROMPT = textwrap.dedent("""
You are analyzing user activity to detect decision loops and recommend interventions.

Given a list of user events, you must:
1. First, classify the loop type (detection phase)
2. Then, recommend an intervention (intervention phase)

Detection actions:
- detect_repeated_search: User searches same/similar queries repeatedly
- detect_revisit: User revisits same content multiple times
- detect_app_switching: User switches between apps indecisively
- continue_monitoring: No clear loop pattern

Intervention actions:
- pause: Suggest taking a break
- decide: Encourage making a decision
- reframe: Help reframe the approach
- continue_monitoring: No intervention needed

Reply with ONLY the action name, nothing else.
""").strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


class LoopBreakerClient:
    """HTTP client for LoopBreaker environment."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = "default"

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if HF_TOKEN:
            h["Authorization"] = f"Bearer {HF_TOKEN}"
        return h

    def reset(self, task_id: str = None) -> dict:
        resp = httpx.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id, "session_id": self.session_id},
            headers=self._headers(),
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()

    def step(self, action_type: str) -> dict:
        resp = httpx.post(
            f"{self.base_url}/step",
            json={"action": {"action_type": action_type}, "session_id": self.session_id},
            headers=self._headers(),
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        pass


def format_events(events: list) -> str:
    lines = []
    for i, e in enumerate(events, 1):
        lines.append(f"{i}. [{e.get('type')}] {e.get('value')}")
    return "\n".join(lines)


def get_action(client: OpenAI, events: list, phase: str, feedback: str = "") -> str:
    """Get action from LLM."""
    events_str = format_events(events)

    if phase == "detection":
        user_prompt = f"Events:\n{events_str}\n\nClassify the loop type. Reply with only the detection action."
    else:
        user_prompt = f"Events:\n{events_str}\n\nPrevious feedback: {feedback}\n\nRecommend an intervention. Reply with only the intervention action."

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=50,
        )
        text = (completion.choices[0].message.content or "").strip().lower()

        # Parse action
        valid_actions = [
            "detect_repeated_search", "detect_revisit", "detect_app_switching",
            "pause", "decide", "reframe", "continue_monitoring"
        ]
        for action in valid_actions:
            if action in text:
                return action
        return "continue_monitoring"
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return "continue_monitoring"


def main() -> None:
    llm = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    env = LoopBreakerClient(ENV_URL)

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = env.reset()
        events = obs.get("recent_events", [])
        done = False
        feedback = ""
        phase = "detection"

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            action = get_action(llm, events, phase, feedback)
            obs = env.step(action)

            reward = obs.get("reward") or 0.0
            done = obs.get("done", False)
            error = None
            feedback = obs.get("feedback", "")

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=action, reward=reward, done=done, error=error)

            # Move to intervention phase after detection
            if phase == "detection" and action in ["detect_repeated_search", "detect_revisit", "detect_app_switching", "continue_monitoring"]:
                phase = "intervention"

            if done:
                break

        total_reward = sum(rewards)
        score = min(max(total_reward / MAX_TOTAL_REWARD, 0.0), 1.0)
        success = score >= 0.5

    except Exception as e:
        print(f"[DEBUG] Error: {e}", flush=True)

    finally:
        env.close()
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
