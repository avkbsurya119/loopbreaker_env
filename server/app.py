from fastapi import FastAPI, HTTPException
from server.models import LoopBreakerAction, StepResult, ResetResult, EnvState
from server.env import LoopBreakerEnv

app = FastAPI(title="LoopBreaker OpenEnv", version="1.0.0")
_env = LoopBreakerEnv()

@app.post("/reset", response_model=ResetResult)
def reset(task_name: str = "easy"):
    return _env.reset(task_name=task_name)

@app.post("/step", response_model=StepResult)
def step(action: LoopBreakerAction):
    try:
        return _env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state", response_model=EnvState)
def state():
    return _env.state()

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
