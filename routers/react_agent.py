from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import re

# Load environment variables
load_dotenv()

# Import tools
import sys
sys.path.append('src')
from react_agent.tools import get_tools, course_details

router = APIRouter()

# Pydantic models for request/response validation
class ReActRequest(BaseModel):
    query: str = Field(..., description="User's question or request")
    model: str = Field(default="gpt-4", description="Model to use (gpt-4, claude-3-sonnet-20240229)")
    max_iterations: int = Field(default=3, description="Maximum reasoning iterations")

class ReActResponse(BaseModel):
    answer: str = Field(..., description="Agent's final answer")
    reasoning_steps: List[str] = Field(default=[], description="Steps taken by the agent")
    tools_used: List[str] = Field(default=[], description="Tools used by the agent")

def create_simple_react_agent(query: str, model: str = "gpt-4", max_iterations: int = 3):
    """
    Simple ReAct agent implementation that doesn't require complex LangGraph setup.
    """
    # Initialize the model
    if model.startswith("gpt"):
        llm = ChatOpenAI(
            model=model,
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif model.startswith("claude"):
        llm = ChatAnthropic(
            model=model,
            temperature=0.2,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        raise ValueError(f"Unsupported model: {model}")
    
    # Get available tools
    tools = get_tools()
    tool_names = [tool.name for tool in tools]

    def is_course_query(text: str) -> bool:
        lowered = text.lower()
        keywords = [
            "course", "syllabus", "instructor", "professor", "schedule", "office hours",
            "prereq", "prerequisite", "credits", "semester", "midterm", "final", "assignments",
        ]
        if any(k in lowered for k in keywords):
            return True
        # Common course-code patterns like CS101, CS 101, MATH-220, etc.
        if re.search(r"\b[A-Z]{2,6}[- ]?\d{2,4}\b", text):
            return True
        return False

    course_context = None
    tools_used = []
    if is_course_query(query):
        try:
            course_context = course_details.invoke(query)
            tools_used.append("course_details")
        except Exception as e:
            course_context = f"Course syllabus retrieval failed: {str(e)}"

    # Create system prompt
    system_prompt = f"""You are a helpful AI assistant that can answer questions and use provided context to be accurate.

Available tools: {', '.join(tool_names)}

If the user's question is about a course, use the provided course syllabus context (if present) as the primary source of truth. If the context is missing or insufficient, say what is missing and what you'd need.

User question: {query}

Course syllabus context:
{course_context if course_context else "(none)"} 

Please provide a clear, helpful answer. If you need to use a tool, mention which one you would use and why."""
    
    # Get response from LLM
    messages = [
        HumanMessage(content=system_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # For now, return a simple response
    # In a full implementation, you would parse the response and execute tools
    return {
        "answer": response.content,
        "reasoning_steps": [response.content],
        "tools_used": tools_used
    }

@router.post("/react", response_model=ReActResponse)
async def react_agent(request: ReActRequest):
    """
    ReAct agent endpoint that can reason, act, and use tools to answer questions.
    
    Args:
        request: ReActRequest containing the user's query and configuration
        
    Returns:
        ReActResponse with the agent's answer and reasoning steps
    """
    try:
        # Validate API key
        api_key = os.getenv("OPENAI_API_KEY") if request.model.startswith("gpt") else os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail=f"{request.model.upper()}_API_KEY environment variable is not set."
            )
        
        # Use simple ReAct agent for now
        result = create_simple_react_agent(
            query=request.query,
            model=request.model,
            max_iterations=request.max_iterations
        )
        
        return ReActResponse(
            answer=result["answer"],
            reasoning_steps=result["reasoning_steps"],
            tools_used=result["tools_used"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ReAct agent error: {str(e)}"
        )
