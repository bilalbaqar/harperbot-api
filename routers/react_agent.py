from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()

# Import tools
import sys
sys.path.append('src')
from react_agent.tools import get_tools

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
    
    # Create system prompt
    system_prompt = f"""You are a helpful AI assistant that can reason about questions and use tools to find answers.

Available tools: {', '.join(tool_names)}

Think step by step about what you need to do to answer the user's question. You can use tools if needed.

User question: {query}

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
        "tools_used": []
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
