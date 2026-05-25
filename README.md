# HarperBot API

FastAPI backend for HarperBot — Chicago Booth MBA course assistant powered by Claude claude-sonnet-4-6.

## Local Development

```bash
# 1. Create .env
cp .env.example .env
# Add your ANTHROPIC_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API
uvicorn main:app --reload --port 8000

# 4. Test it
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What courses fulfill the Decisions requirement?", "conversation_history": []}'
```
<<<<<<< Updated upstream
harperbot-api/
├── main.py              # Application entry point
├── routers/             # Route organization
│   ├── __init__.py
│   ├── health.py        # Health check endpoints
│   ├── chat.py          # Chat endpoints with OpenAI integration
│   └── react_agent.py   # ReAct agent endpoints
├── src/react_agent/     # ReAct agent implementation
│   ├── __init__.py
│   ├── graph.py         # Main agent graph
│   ├── tools.py         # Available tools
│   └── prompts.py       # System prompts
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```
=======
>>>>>>> Stashed changes

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Main chat endpoint |
| GET | `/api/examples` | Sample questions |

### POST `/api/chat`

<<<<<<< Updated upstream
### ReAct Agent
- **POST** `/react`
  - Request Body:
    ```json
    {
      "query": "What's the weather like in New York?",
      "model": "gpt-4",
      "max_iterations": 5
    }
    ```
  - Returns: 
    ```json
    {
      "answer": "Based on my search, the weather in New York is...",
      "reasoning_steps": ["Step 1: I need to search for current weather...", "Step 2: Found weather information..."],
      "tools_used": ["search_web"]
    }
    ```
  - Purpose: Advanced reasoning agent that can use tools to answer complex questions
  - Features:
    - ReAct (Reasoning + Acting) architecture based on LangGraph
    - Available tools: web search, calculator, time lookup, weather lookup
    - Supports both OpenAI and Anthropic models
    - Step-by-step reasoning with tool usage
=======
**Request:**
```json
{
  "message": "What are the bid points for 35000?",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```
>>>>>>> Stashed changes

**Response:**
```json
{
  "response": "Here is the bidding history for 35000 — Investments...",
  "tool_calls": [
    {"tool": "get_bid_history", "input": {"course_number": "35000"}, "result_preview": "..."}
  ]
}
```

## Deploy to Railway

1. Push this directory to a GitHub repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Set env var: `ANTHROPIC_API_KEY`
4. Railway auto-deploys on every push

## Tools Available

| Tool | Description |
|------|-------------|
| `check_degree_requirements` | MBA degree requirements checker |
| `check_concentration_requirements` | Concentration requirements checker |
| `search_courses` | Full-text course search (title, instructor, time, quarter) |
| `lookup_course_by_number` | Get all sections for a course number |
| `get_course_title` | Course number → title lookup |
| `get_bid_history` | Bidding point history for a course |
| `search_bidding_by_name` | Find course number from name for bidding lookup |

## Data

CSV files in `data/` are loaded at startup:
- `all-course-list.csv` — 619 course offerings (Winter 2025, Spring 2025, etc.)
- `bidding-history.csv` — 1,278 historical bidding records
