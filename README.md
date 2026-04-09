# LoopBreaker — OpenEnv Environment

## Overview
LoopBreaker simulates a real-world task: detecting and intervening in human decision-making loops.
People often get stuck in repetitive thinking patterns — searching the same thing, revisiting content,
or switching apps indecisively. This environment trains AI agents to recognize those patterns and
suggest the optimal intervention.

## Motivation
Decision-loop detection has direct applications in digital wellness, productivity software,
and cognitive behavioral tools. This env fills a gap in OpenEnv's coverage of psychological
and behavioral domains.

## Action Space
| Field | Type | Values |
|---|---|---|
| `intervention` | string | `decide`, `pause`, `reframe`, `monitor`, `escalate` |
| `reason` | string (optional) | Agent's explanation |
| `confidence` | float | 0.0 – 1.0 |

## Observation Space
| Field | Type | Description |
|---|---|---|
| `current_behavior_sequence` | list[str] | Last N user actions |
| `loop_detected` | bool | Whether a loop was found |
| `loop_type` | str or null | `search_repeat`, `content_revisit`, `app_switch` |
| `loop_depth` | int | How many times the pattern repeated |
| `suggested_action` | str or null | Agent's last intervention |
| `step_number` | int | Current step |
| `task_description` | str | Task instructions |
| `time_elapsed` | int | Simulated seconds in session |

## Tasks
| Task | Difficulty | Max Steps | Description |
|---|---|---|---|
| `easy` | Easy | 5 | Simple repeated-search loop. Correct action: `decide` |
| `medium` | Medium | 8 | App-switch or content-revisit loop. Choose `pause` or `reframe` |
| `hard` | Hard | 12 | Compound multi-modal loop. All types, best intervention, confidence ≥ 0.8 |

## Reward Function
- Provides signal at every step (not just end-of-episode)
- Rewards correct intervention weighted by confidence
- Awards partial credit for monitoring or near-correct choices
- Penalizes clearly wrong or looping actions (reward = 0.0)

## Baseline Scores
| Task | Baseline Score |
|---|---|
| easy | ~0.75 |
| medium | ~0.55 |
| hard | ~0.30 |

## Setup & Usage

### Local run
```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 7860
```

### Docker
```bash
docker build -t loopbreaker .
docker run -p 7860:7860 loopbreaker
```

### Run inference baseline
```bash
export HF_TOKEN=your_token
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export API_BASE_URL=https://router.huggingface.co/v1
export LOOPBREAKER_ENV_URL=http://localhost:7860
python inference.py
```

### API Endpoints
- `POST /reset?task_name=easy` — Start new episode
- `POST /step` — Submit action, get observation + reward
- `GET /state` — Get current environment state
- `GET /health` — Health check
