from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from .debate import run_debate
    from .models import DebateRequest, DebateResponse
except ImportError:
    from debate import run_debate
    from models import DebateRequest, DebateResponse

app = FastAPI(
    title="AI vs AI Debate Simulator API",
    description="Backend API for running multi-round AI debates with automated judging.",
    version="1.0.0",
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "AI vs AI Debate Simulator API is running",
    }


@app.post("/debate", response_model=DebateResponse)
def debate_endpoint(request: DebateRequest) -> DebateResponse:
    """Run a multi-round debate on the specified topic and return full transcript and verdict."""
    return run_debate(topic=request.topic, num_rounds=request.num_rounds)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
