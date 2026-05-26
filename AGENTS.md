# HarperBot API — Agent Context

This is the single source of truth for AI coding assistants. It is read directly by agents that look for `AGENTS.md` (e.g., OpenAI Codex, Gemini). Claude Code users are pointed here via `CLAUDE.md`, which contains a single `@AGENTS.md` import — so this file loads automatically when opening the project in Claude Code.

---

## What This Is

**HarperBot** is a chatbot for University of Chicago Booth School of Business MBA students, accessible at [harperbot.com](https://harperbot.com). It answers questions about:

- MBA degree requirements and how to fulfill them
- Concentration requirements (14 concentrations)
- Course schedules, instructors, locations, and enrollment
- Bidding history and strategy (BIDP — Booth's bid-point system)

The chatbot is named after **Harper Center**, Booth's main building on the Hyde Park campus.

---

## Architecture

```
Frontend (harperbot.com — Vercel)
        │
        │ POST /api/chat
        ▼
Backend (Railway — this repo)
  FastAPI + Python 3.11+
        │
        │ Anthropic Messages API (tool_use)
        ▼
  Claude claude-sonnet-4-6
        │
        ├── check_degree_requirements       → tools/degree_requirements.py
        ├── check_concentration_requirements→ tools/degree_requirements.py
        ├── search_courses                  → tools/course_search.py
        ├── lookup_course_by_number         → tools/course_search.py
        ├── get_course_title                → tools/course_search.py
        ├── get_bid_history                 → tools/bidding_history.py
        └── search_bidding_by_name          → tools/bidding_history.py
```

Data is loaded from CSVs in `data/` into pandas DataFrames at startup — no external database in v1.

---

## File Map

```
harperbot-api/
├── main.py                     FastAPI app. Routes: GET /health, POST /api/chat, GET /api/examples
├── agent.py                    Claude tool_use loop. Core logic: run_agent(message, history) → dict
├── tools/
│   ├── degree_requirements.py  Hardcoded MBA degree + concentration requirements as strings.
│   │                           get_degree_requirements(query) and get_concentration_requirements(query)
│   │                           return the full requirements text for Claude to reason over.
│   ├── course_search.py        Pandas-backed course search on all-course-list.csv.
│   │                           Functions: search_courses(), lookup_course_by_number(),
│   │                           get_course_title(), list_courses_by_quarter()
│   └── bidding_history.py      Pandas-backed bid history on bidding-history.csv.
│                               Functions: get_bid_history(course_number),
│                               search_bidding_by_name(course_name)
├── data/
│   ├── all-course-list.csv     619 rows. Columns: Quarter, Title, Course, Section, Program,
│   │                           Faculty, Schedule, Capacity (format: "current/max"), Building, Location
│   └── bidding-history.csv     1,278 rows. Key columns: Course_Number, Title, Quarter, Year,
│                               Phase 1 Price, Phase 2 Price, Phase 3 Price (numeric, NaN if unavailable)
├── scripts/
│   └── test_local.py           Smoke tests. Runs tool functions directly (no LLM), then one
│                               full agent call. Run from api/ dir: python scripts/test_local.py
├── requirements.txt            anthropic, fastapi, uvicorn, pydantic, pandas, python-dotenv, httpx
├── Procfile                    Railway start command: uvicorn main:app --host 0.0.0.0 --port $PORT
└── railway.json                Railway deploy config (Nixpacks builder, /health healthcheck)
```

---

## Key Design Decisions

**Why pandas instead of a vector DB?**
The course list is 619 rows and bidding history is 1,278 rows — small enough to load in memory and query with text search in milliseconds. Adding pgvector (Supabase) is a planned future improvement but was intentionally skipped for the v1 12-hour build.

**Why Claude tool_use instead of LangChain?**
The original `booth-chatbot` prototype (in `../booth-chatbot/`) used LangChain ReAct. This rewrite uses the Anthropic SDK directly for simplicity, fewer dependencies, and better reliability. The tool loop is in `agent.py:run_agent()`.

**Why hardcoded degree/concentration requirements?**
The data doesn't change often (once per academic year). Hardcoding avoids a DB lookup and lets Claude reason over the full requirements text in one shot. The data lives in `tools/degree_requirements.py` as `DEGREE_REQUIREMENTS` and `CONCENTRATION_REQUIREMENTS` strings.

**Conversation history model**
The frontend maintains history and sends it with each request as `conversation_history: [{role, content}]`. The backend is stateless — no session storage. Only text messages should be in history (not raw tool_use blocks).

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | From console.anthropic.com |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins. Defaults to `*` for now. |

---

## Running Locally

```bash
pip install -r requirements.txt

# Create .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Start server
uvicorn main:app --reload --port 8000

# Test the endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the bid points for Investments?", "conversation_history": []}'

# Smoke test tools without LLM calls
python scripts/test_local.py
```

---

## Deployment

**Backend → Railway**
- Auto-deploys on push to `main`
- Set `ANTHROPIC_API_KEY` in Railway Variables tab
- Health check: `GET /health`

**Frontend → Vercel**
- Built with Lovable (prompt in `../LOVABLE_PROMPT.md`)
- Env var: `VITE_API_URL=https://<railway-url>`
- Custom domain: harperbot.com

---

## The Original Prototype

The original exploration code lives in `../booth-chatbot/` (a separate git repo). It used:
- LangChain ReAct agent
- GPT-4o-mini / GPT-4
- FAISS for syllabus PDF RAG
- Streamlit frontend
- Flask backend

This repo (`harperbot-api`) is a clean rewrite keeping the same tool concepts but with a simpler, deployable stack.

---

## Planned Features (Not Yet Built)

| Feature | Notes |
|---------|-------|
| Syllabus RAG | Upload PDFs → chunk → embed → Supabase pgvector. Only 3 syllabi in prototype. |
| Real-time course data | Scrape Booth registrar or use their API if available. |
| User accounts | Personalized course planning, saved searches. |
| Bidding strategy AI | Trend analysis, percentile recommendations. |
| Admin data refresh | Update CSVs via UI without redeploying. |
| `harperbot-ui` repo | Lovable-generated React frontend (separate repo, deploys to Vercel). |

---

## Data Notes

**`all-course-list.csv`**
- Source: Booth course schedule (manually exported)
- Covers: Winter 2025, Spring 2025, some Autumn 2024 and Summer terms
- `Capacity` format: `"48/65"` = 48 enrolled / 65 max. `"CLO"` = closed.
- `Course` column = 5-digit course number (string, e.g., `"35150"`)

**`bidding-history.csv`**
- Source: BIDP historical data (manually exported)
- `Phase 1 Price` = points to guarantee a seat in Phase 1 bidding
- `Phase 2 Price` = points needed in Phase 2 (typically higher for popular courses)
- `Phase 3 Price` = clearing price in Phase 3 (open bidding)
- `0` means the course was available for free (no points needed)
- `NaN` means no data for that phase
- Popular courses like `35000` (Investments) hit 13,000+ points in Phase 2
