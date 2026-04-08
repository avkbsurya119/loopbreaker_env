---
title: LoopBreaker Environment
emoji: 🔄
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 8000
---

# LoopBreaker Environment

LoopBreaker is an OpenEnv environment for detecting overthinking and decision loops.

## Problem

People often get stuck in repetitive digital behavior patterns such as:
- Repeated searches for the same topic
- Revisiting the same content multiple times
- Indecisive switching between apps

These patterns indicate decision paralysis or overthinking that can reduce productivity.

## Goal

The agent must:
1. Identify whether the current behavior represents a loop state
2. Classify the type of loop (repeated search, revisiting content, app switching)
3. Recommend the best intervention (pause, decide, or reframe)

## Tasks

The environment includes 18 scenarios across 4 categories:

### Loop Categories
1. **Repeated Search** - User searches for the same/similar queries multiple times
2. **Revisiting Content** - User keeps returning to the same pages or articles
3. **App Switching** - User oscillates between apps without productive work
4. **No Loop** - Normal productive behavior (for testing false positives)

### Difficulty Levels
- **Easy**: Clear, obvious patterns
- **Medium**: Patterns with some noise or variation
- **Hard**: Subtle patterns mixed with normal activity

## Action Space

### Detection Actions
- `detect_repeated_search`: Identify repeated search behavior
- `detect_revisit`: Identify content revisiting behavior
- `detect_app_switching`: Identify app switching behavior
- `continue_monitoring`: No clear loop detected

### Intervention Actions
- `pause`: Recommend taking a break
- `decide`: Encourage making a decision
- `reframe`: Help reframe the approach
- `continue_monitoring`: No intervention needed

## Evaluation

The environment rewards:
- **+1.0** for correct loop detection
- **+1.0** for correct intervention recommendation
- **+0.5** early detection bonus (step 1)
- **+0.25** early detection bonus (step 2)
- **+0.25** for acceptable but non-optimal intervention
- **-0.5** for wrong detection or intervention
- **-1.0** for invalid actions

Total possible reward per episode: **2.5** (perfect detection + intervention with early bonus)

## Installation

```bash
pip install -e .
```

## Usage

### Start the Server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Use the Client

```python
from loopbreaker_env.client import LoopBreakerEnv
from loopbreaker_env.models import LoopBreakerAction

# Synchronous usage
with LoopBreakerEnv(base_url="http://localhost:8000").sync() as env:
    # Reset to start a new episode
    obs = env.reset()
    print(f"Task: {obs.task_id}")
    print(f"Events: {obs.recent_events}")

    # Take a detection action
    action = LoopBreakerAction(action_type="detect_repeated_search")
    obs = env.step(action)
    print(f"Reward: {obs.reward}, Feedback: {obs.feedback}")

    # Take an intervention action
    action = LoopBreakerAction(action_type="decide")
    obs = env.step(action)
    print(f"Done: {obs.done}, Final Reward: {obs.reward}")
```

### Async Usage

```python
import asyncio
from loopbreaker_env.client import LoopBreakerEnv
from loopbreaker_env.models import LoopBreakerAction

async def main():
    async with LoopBreakerEnv(base_url="http://localhost:8000") as env:
        obs = await env.reset()
        print(obs)

asyncio.run(main())
```

## API Endpoints

- `GET /health` - Health check
- `GET /info` - Environment information
- `GET /tasks` - List all tasks
- `GET /tasks/{task_id}` - Get task details
- `POST /reset` - Reset environment
- `POST /step` - Execute action
- `GET /state` - Get current state
- `GET /docs` - OpenAPI documentation

## Docker

```bash
# Build
docker build -t loopbreaker_env -f server/Dockerfile .

# Run
docker run -p 8000:8000 loopbreaker_env
```

## License

MIT
