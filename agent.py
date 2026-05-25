"""
HarperBot Agent — Claude claude-sonnet-4-6 with tool_use.
Manages the multi-turn tool loop until Claude reaches a final answer.
"""
import os
import json
from typing import Any
import anthropic

from tools.degree_requirements import get_degree_requirements, get_concentration_requirements
from tools.course_search import (
    search_courses,
    lookup_course_by_number,
    get_course_title,
    list_courses_by_quarter,
)
from tools.bidding_history import get_bid_history, search_bidding_by_name

# ---------------------------------------------------------------------------
# Claude client
# ---------------------------------------------------------------------------
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are HarperBot, a friendly and knowledgeable assistant for students at the University of Chicago Booth School of Business. You are named after Harper Center, Booth's home.

Your expertise covers:
- MBA degree requirements and how to fulfill them
- Concentration requirements and course eligibility
- Course schedules, instructors, room locations, and enrollment
- Bidding history and strategy for the BIDP (Booth Integrated Dual Priority) system
- General Booth program questions

When answering:
1. Always be accurate — use the tools to look up real data rather than guessing
2. When you mention a course number, also mention its title if known
3. For bidding questions, give concrete data (actual point ranges from history) and practical recommendations
4. Keep answers concise but complete — use bullet points or tables for lists
5. If a student asks about a course by name but you need the number, use the course search tool first
6. Be warm and supportive — Booth can be stressful!

You have tools to look up live Booth data. Always use them when the question is about specific courses, requirements, or bids.
"""

# ---------------------------------------------------------------------------
# Tool definitions (Claude tool_use schema)
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "check_degree_requirements",
        "description": (
            "Look up MBA degree requirements at Booth. Use this when a student asks "
            "what courses fulfill a specific requirement (e.g., Finance, Decisions, Statistics, "
            "Financial Accounting, Microeconomics) or what the core requirements are."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The student's question about degree requirements",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_concentration_requirements",
        "description": (
            "Look up concentration requirements at Booth. Use this when a student asks "
            "whether a course counts toward a concentration (Finance, Marketing, Entrepreneurship, etc.) "
            "or what courses are needed for a specific concentration."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The student's question about concentration requirements",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_courses",
        "description": (
            "Search for courses by keyword. Works on course title, instructor name, "
            "course number, quarter (e.g., 'Spring 2025'), day/time, or program. "
            "Use this to find when a course is offered, who teaches it, where it meets, "
            "or to get a list of courses matching a topic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term — e.g., 'Investments', 'Stefan Nagel', 'Monday evening', 'Spring 2025'",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 10)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "lookup_course_by_number",
        "description": (
            "Get all scheduled sections for a specific course number. "
            "Returns all quarters, instructors, schedules, and enrollment capacities."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "course_number": {
                    "type": "string",
                    "description": "The 5-digit Booth course number, e.g., '35150'",
                }
            },
            "required": ["course_number"],
        },
    },
    {
        "name": "get_course_title",
        "description": "Get the title/name of a course given its course number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "course_number": {
                    "type": "string",
                    "description": "The 5-digit Booth course number",
                }
            },
            "required": ["course_number"],
        },
    },
    {
        "name": "get_bid_history",
        "description": (
            "Get the bidding point history for a course. Returns Phase 1, 2, and 3 "
            "bid prices across multiple quarters, plus summary statistics. "
            "Use this when students ask how many points they need to bid, "
            "what the typical bid is, or bidding strategy for a course."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "course_number": {
                    "type": "string",
                    "description": "The 5-digit Booth course number, e.g., '35150'",
                }
            },
            "required": ["course_number"],
        },
    },
    {
        "name": "search_bidding_by_name",
        "description": (
            "Search bidding history by course name when you don't have the course number. "
            "Returns matching courses with their numbers so you can then call get_bid_history."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "course_name": {
                    "type": "string",
                    "description": "Full or partial course name, e.g., 'Investments', 'Negotiations'",
                }
            },
            "required": ["course_name"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------
def _execute_tool(name: str, inputs: dict) -> str:
    """Execute a tool call and return string result."""
    try:
        if name == "check_degree_requirements":
            return get_degree_requirements(inputs["query"])
        elif name == "check_concentration_requirements":
            return get_concentration_requirements(inputs["query"])
        elif name == "search_courses":
            return search_courses(inputs["query"], inputs.get("max_results", 10))
        elif name == "lookup_course_by_number":
            return lookup_course_by_number(inputs["course_number"])
        elif name == "get_course_title":
            return get_course_title(inputs["course_number"])
        elif name == "get_bid_history":
            return get_bid_history(inputs["course_number"])
        elif name == "search_bidding_by_name":
            return search_bidding_by_name(inputs["course_name"])
        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool error in {name}: {str(e)}"


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------
def run_agent(user_message: str, conversation_history: list[dict]) -> dict[str, Any]:
    """
    Run the Claude agent with tool_use loop.

    Args:
        user_message: The latest user message
        conversation_history: List of prior {role, content} messages (for multi-turn)

    Returns:
        dict with 'response' (str), 'tool_calls' (list), 'updated_history' (list)
    """
    messages = conversation_history + [{"role": "user", "content": user_message}]
    tool_calls_log = []
    max_iterations = 10  # Safety limit

    for _ in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Collect tool use blocks
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if response.stop_reason == "end_turn" or not tool_use_blocks:
            # Extract final text response
            text_blocks = [b for b in response.content if b.type == "text"]
            final_response = text_blocks[-1].text if text_blocks else "I couldn't generate a response."

            # Update history with final exchange
            updated_history = messages + [{"role": "assistant", "content": response.content}]

            return {
                "response": final_response,
                "tool_calls": tool_calls_log,
                "updated_history": updated_history,
            }

        # Execute all tool calls
        tool_results = []
        for block in tool_use_blocks:
            result = _execute_tool(block.name, block.input)
            tool_calls_log.append({
                "tool": block.name,
                "input": block.input,
                "result_preview": result[:200] + "..." if len(result) > 200 else result,
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        # Add assistant turn (with tool_use blocks) and tool results to messages
        messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ]

    return {
        "response": "I hit my iteration limit. Please try rephrasing your question.",
        "tool_calls": tool_calls_log,
        "updated_history": messages,
    }
