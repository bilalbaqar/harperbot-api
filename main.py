"""
HarperBot API — FastAPI backend
Endpoint: POST /api/chat
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from agent import run_agent

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="HarperBot API",
    description="Chicago Booth MBA Course Assistant",
    version="1.0.0",
)

# CORS — allow your Vercel frontend and localhost during dev
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://harperbot.com,https://www.harperbot.com",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten after launch
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[list[Message]] = []


class ChatResponse(BaseModel):
    response: str
    tool_calls: list[dict]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "HarperBot API"}


@app.get("/health")
def health():
    return {"status": "healthy", "model": "claude-sonnet-4-6"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint.

    Send the latest user message plus conversation history.
    Returns the assistant's response and a log of tool calls made.

    Conversation history format:
      [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Note: Only include text-based messages in history (not raw tool use blocks).
    The frontend should store conversation history and send it back each turn.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Convert Pydantic models to plain dicts for the agent
    history = [{"role": m.role, "content": m.content} for m in (req.conversation_history or [])]

    try:
        result = run_agent(req.message, history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    return ChatResponse(
        response=result["response"],
        tool_calls=result["tool_calls"],
    )


@app.get("/api/examples")
def get_examples():
    """Return example questions for the frontend to display."""
    return {
        "examples": [
            "What courses can I take to fulfill the Decisions requirement?",
            "Does 30131 fulfill requirements for the Accounting concentration?",
            "When is Investments offered next?",
            "What are the bid points for 35150?",
            "What courses are offered on Monday evenings in Spring 2025?",
            "How many points do I need for Negotiations?",
            "What courses count towards the Finance concentration?",
            "Who is teaching Advanced Investments?",
            "What are my options for the Statistics requirement?",
            "What courses has Stefan Nagel taught?",
        ]
    }
