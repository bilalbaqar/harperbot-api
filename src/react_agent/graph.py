"""
ReAct agent graph implementation.
"""

from typing import Dict, List, Tuple, Any, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

from .tools import get_tools
from .prompts import get_prompts


class AgentState(TypedDict):
    """State schema for the ReAct agent."""
    messages: List[BaseMessage]
    current_step: int
    max_steps: int
    tool_results: List[Dict[str, Any]]
    final_answer: str


def create_react_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.2,
    max_iterations: int = 10
) -> StateGraph:
    """
    Create a ReAct agent graph.
    
    Args:
        model_name: The model to use for reasoning
        temperature: Temperature for model responses
        max_iterations: Maximum number of reasoning iterations
        
    Returns:
        StateGraph: The configured ReAct agent
    """
    
    # Initialize the model
    if model_name.startswith("gpt"):
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif model_name.startswith("claude"):
        llm = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    
    # Get tools and prompts
    tools = get_tools()
    prompts = get_prompts()
    
    # Create tool executor
    tool_executor = ToolExecutor(tools)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("reason", reason_node(llm, prompts))
    workflow.add_node("act", act_node(tool_executor))
    workflow.add_node("should_continue", should_continue_node)
    workflow.add_node("final_answer", final_answer_node(llm, prompts))
    
    # Add edges
    workflow.add_edge("reason", "act")
    workflow.add_edge("act", "should_continue")
    workflow.add_conditional_edges(
        "should_continue",
        lambda x: "reason" if x["current_step"] < x["max_steps"] else "final_answer"
    )
    workflow.add_edge("final_answer", END)
    
    # Set entry point
    workflow.set_entry_point("reason")
    
    return workflow.compile()


def reason_node(llm, prompts):
    """Node for reasoning about the next action."""
    
    def _reason(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        current_step = state["current_step"]
        
        # Create reasoning prompt
        reasoning_prompt = prompts["reasoning"].format(
            messages=messages,
            current_step=current_step,
            max_steps=state["max_steps"]
        )
        
        # Get reasoning from LLM
        reasoning_response = llm.invoke(reasoning_prompt)
        
        # Add reasoning to messages
        messages.append(AIMessage(content=reasoning_response.content))
        
        return {
            "messages": messages,
            "current_step": current_step + 1
        }
    
    return _reason


def act_node(tool_executor):
    """Node for executing tools."""
    
    def _act(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        tool_results = state.get("tool_results", [])
        
        # Extract tool call from last message
        last_message = messages[-1]
        
        # Parse tool call (simplified - in practice you'd use a more robust parser)
        tool_name, tool_args = parse_tool_call(last_message.content)
        
        if tool_name:
            # Execute tool
            result = tool_executor.invoke({
                "tool": tool_name,
                "tool_input": tool_args
            })
            
            tool_results.append({
                "tool": tool_name,
                "input": tool_args,
                "output": result
            })
            
            # Add tool result to messages
            messages.append(HumanMessage(content=f"Tool result: {result}"))
        
        return {
            "messages": messages,
            "tool_results": tool_results
        }
    
    return _act


def should_continue_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node to determine if we should continue reasoning."""
    return state


def final_answer_node(llm, prompts):
    """Node for generating final answer."""
    
    def _final_answer(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        tool_results = state.get("tool_results", [])
        
        # Create final answer prompt
        final_prompt = prompts["final_answer"].format(
            messages=messages,
            tool_results=tool_results
        )
        
        # Get final answer from LLM
        final_response = llm.invoke(final_prompt)
        
        return {
            "final_answer": final_response.content
        }
    
    return _final_answer


def parse_tool_call(content: str) -> Tuple[str, str]:
    """Parse tool call from LLM response."""
    # This is a simplified parser - in practice you'd use a more robust approach
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith("Tool:"):
            parts = line.split(":", 2)
            if len(parts) >= 3:
                tool_name = parts[1].strip()
                tool_args = parts[2].strip()
                return tool_name, tool_args
    return None, None
