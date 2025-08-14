# HarperBot API

A FastAPI-based REST API for the HarperBot application.

## Features

- FastAPI framework for high-performance API development
- Modular router structure for organized code
- CORS middleware with permissive settings for development
- Health check endpoint
- Automatic API documentation

## Project Structure

```
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

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns: `{"status": "ok"}`
  - Purpose: Health monitoring and API status verification

### Chat
- **POST** `/chat`
  - Request Body:
    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "Hello, how are you?"
        }
      ]
    }
    ```
  - Returns: `{"response": "I'm doing well, thank you for asking!"}`
  - Purpose: Generate AI responses using OpenAI GPT-5 responses API
  - Features:
    - Uses GPT-5 responses API with minimal reasoning effort
    - Takes the last user message as input
    - Comprehensive error handling

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

## Development

The API runs on `http://localhost:8000` by default.

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### CORS Settings
The API includes permissive CORS settings for development:
- All origins allowed (`*`)
- All methods allowed
- All headers allowed
- Credentials enabled

**Note**: These settings are for development only. Configure more restrictive CORS settings for production.

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
