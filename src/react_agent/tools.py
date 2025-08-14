"""
Tools for the ReAct agent.
"""

from langchain_core.tools import tool
import math
import datetime

# Try to import Tavily, but provide fallback if not available
try:
    from langchain_community.tools import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


@tool
def search_web(query: str) -> str:
    """
    Search the web for current information.
    
    Args:
        query: The search query
        
    Returns:
        str: Search results
    """
    if not TAVILY_AVAILABLE:
        return f"Web search not available. Please install tavily-python and set TAVILY_API_KEY. Query was: {query}"
    
    try:
        search_tool = TavilySearchResults(max_results=3)
        results = search_tool.invoke(query)
        return str(results)
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def calculator(expression: str) -> str:
    """
    Evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        str: Result of the calculation
    """
    try:
        # Remove any potentially dangerous operations
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def get_current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        str: Current date and time
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def weather_lookup(city: str) -> str:
    """
    Get weather information for a city.
    Note: This is a placeholder - you would integrate with a real weather API.
    
    Args:
        city: City name
        
    Returns:
        str: Weather information
    """
    # This is a placeholder - in practice you'd call a weather API
    return f"Weather information for {city}: This is a placeholder. In a real implementation, you would integrate with a weather API like OpenWeatherMap."


def get_tools():
    """Get all available tools."""
    return [
        search_web,
        calculator,
        get_current_time,
        weather_lookup
    ]
