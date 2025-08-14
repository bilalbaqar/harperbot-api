"""
Prompts for the ReAct agent.
"""


def get_prompts():
    """Get all prompts for the ReAct agent."""
    
    reasoning_prompt = """You are a helpful AI assistant that can reason about questions and use tools to find answers.

Available tools:
- search_web: Search the web for current information
- calculator: Evaluate mathematical expressions
- get_current_time: Get the current date and time
- weather_lookup: Get weather information for a city

Current conversation:
{messages}

Current step: {current_step} of {max_steps}

Think step by step about what you need to do to answer the user's question. If you need to use a tool, specify it in this format:
Tool: tool_name
Args: tool_arguments

If you have enough information to provide a final answer, respond with:
FINAL_ANSWER: your answer here

Your reasoning:"""

    final_answer_prompt = """Based on the conversation and tool results, provide a comprehensive final answer to the user's question.

Conversation history:
{messages}

Tool results:
{tool_results}

Please provide a clear, helpful final answer:"""

    return {
        "reasoning": reasoning_prompt,
        "final_answer": final_answer_prompt
    }
