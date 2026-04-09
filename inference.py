"""
Inference Script — LoopBreaker OpenEnv
=======================================
MANDATORY env vars:
  API_BASE_URL   The API endpoint for the LLM.
  MODEL_NAME     The model identifier.
  HF_TOKEN       Your Hugging Face / API key.
  IMAGE_NAME     Docker image name (if using from_docker_image).

stdout FORMAT (strictly required):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import asyncio
import os
import json
import textwrap
from typing import List, Optional

import httpx
from openai import OpenAI

API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL      = os.getenv("LOOPBREAKER_ENV_URL", "http://localhost:7860")
TASK_NAME    = os.getenv("LOOPBREAKER_TASK", "easy")
BENCHMARK    = "loopbreaker"
MAX_STEPS    = 12
TEMPERATURE  = 0.3
MAX_TOKENS   = 256
SUCCESS_SCORE_THRESHOLD = 0.5

SYSTEM_PROMPT = textwrap.dedent("""
    You are an AI agent interacting with the LoopBreaker environment.
    Each step you receive a JSON observation showing a user's behavior sequence.
    Your job is to:
    1. Detect if the user is stuck in a decision loop.
    2. Choose the best intervention from: decide, pause, reframe, monitor, escalate.
    3. State your reason briefly.
    4. Give a confidence score between 0.0 and 1.0.

    Respond ONLY with a valid JSON object. No markdown, no explanation outside JSON.
    Format:
    {"intervention": "decide", "reason": "User searched same query 3 times.", "confidence": 0.9}
""").strip()


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def get_agent_action(client: OpenAI, observation: dict, step: int, history: List[str]) -> dict:
    history_block = "\n".join(history[-4:]) if history else "None"
    user_msg = f"Step: {step}\nObservation: {json.dumps(observation, indent=2)}\nHistory:\n{history_block}\nWhat is your action?"
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (resp.choices[0].message.content or "").strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as exc:
        print(f"[DEBUG] Model error: {exc}", flush=True)
        return {"intervention": "monitor", "reason": "fallback", "confidence": 0.5}


async def run_task(task_name: str) -> dict:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False
    history = []

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    async with httpx.AsyncClient(base_url=ENV_URL, timeout=30) as http:
        # Reset environment
        r = await http.post("/reset", params={"task_name": task_name})
        r.raise_for_status()
        obs = r.json()["observation"]

        for step in range(1, MAX_STEPS + 1):
            # Get agent action via LLM
            action_dict = get_agent_action(client, obs, step, history)

            # Send action to environment
            try:
                r2 = await http.post("/step", json=action_dict)
                r2.raise_for_status()
                result = r2.json()
            except Exception as e:
                log_step(step=step, action=str(action_dict), reward=0.0, done=True, error=str(e))
                break

            reward = result.get("reward", 0.0)
            done   = result.get("done", False)
            obs    = result["observation"]
            error  = None

            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=str(action_dict.get("intervention", "")),
                     reward=reward, done=done, error=error)

            history.append(f"Step {step}: {action_dict} -> reward {reward:.2f}")

            if done:
                break

    score = max(rewards) if rewards else 0.0   # use best-step score
    score = round(min(max(score, 0.0), 1.0), 3)
    success = score >= SUCCESS_SCORE_THRESHOLD
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {"task": task_name, "score": score, "success": success}


async def main():
    tasks = ["easy", "medium", "hard"]
    results = []
    for task in tasks:
        result = await run_task(task)
        results.append(result)
    print(f"\n[SUMMARY] {results}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
