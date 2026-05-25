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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Main chat endpoint |
| GET | `/api/examples` | Sample questions |

### POST `/api/chat`

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

1. Push this repo to GitHub
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

## Project Structure

```
harperbot-api/
├── main.py                    # FastAPI app, /api/chat endpoint
├── agent.py                   # Claude claude-sonnet-4-6 tool_use loop
├── tools/
│   ├── degree_requirements.py # Hardcoded MBA degree + concentration data
│   ├── course_search.py       # Pandas search on all-course-list.csv
│   └── bidding_history.py     # Pandas query on bidding-history.csv
├── data/
│   ├── all-course-list.csv    # 619 course offerings
│   └── bidding-history.csv    # 1,278 bidding records
├── scripts/
│   └── test_local.py          # Smoke test (no LLM + LLM)
├── requirements.txt
├── Procfile                   # Railway start command
└── railway.json               # Railway config
```

## Data

CSV files in `data/` are loaded at startup into pandas DataFrames:
- `all-course-list.csv` — 619 course offerings (Winter 2025, Spring 2025, etc.)
- `bidding-history.csv` — 1,278 historical bidding records
