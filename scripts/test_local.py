"""
Quick smoke test — run from the api/ directory:
  python scripts/test_local.py

Requires ANTHROPIC_API_KEY in .env or environment.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from tools.course_search import search_courses, lookup_course_by_number, get_course_title
from tools.bidding_history import get_bid_history, search_bidding_by_name

print("=== Tool Smoke Tests (no LLM calls) ===\n")

print("1. search_courses('Investments'):")
print(search_courses("Investments", max_results=3))
print()

print("2. lookup_course_by_number('35150'):")
print(lookup_course_by_number("35150"))
print()

print("3. get_course_title('35150'):")
print(get_course_title("35150"))
print()

print("4. get_bid_history('35150'):")
print(get_bid_history("35150"))
print()

print("5. search_bidding_by_name('Investments'):")
print(search_bidding_by_name("Investments"))
print()

print("=== Agent Test (LLM call) ===\n")
from agent import run_agent

result = run_agent("What courses can I take to fulfill the Decisions requirement?", [])
print("Response:", result["response"][:500])
print("Tools used:", [t["tool"] for t in result["tool_calls"]])
