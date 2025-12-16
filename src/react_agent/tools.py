"""
Tools for the ReAct agent.
"""

from langchain_core.tools import tool
import math
import datetime
import os
import json
from typing import Any, Dict, Optional, Tuple, List

from openai import OpenAI

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


def _get_openai_embedding(text: str) -> List[float]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set (required to embed queries for vector search).")
    client = OpenAI(api_key=api_key)
    resp = client.embeddings.create(model=os.getenv("COURSE_EMBEDDING_MODEL", "text-embedding-3-small"), input=text)
    return resp.data[0].embedding


def _pinecone_query(query: str, top_k: int = 5) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Query Pinecone for relevant syllabus chunks.

    Returns (matches, warning). If Pinecone isn't configured, matches=[] and warning is set.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX")
    if not api_key or not index_name:
        return [], "Pinecone is not configured (set PINECONE_API_KEY and PINECONE_INDEX)."

    namespace = os.getenv("PINECONE_NAMESPACE") or None
    host = os.getenv("PINECONE_HOST") or None
    environment = os.getenv("PINECONE_ENVIRONMENT") or os.getenv("PINECONE_ENV") or None

    embedding = _get_openai_embedding(query)

    # Support both new `pinecone` SDK (Pinecone class) and older `pinecone-client`.
    try:
        from pinecone import Pinecone  # type: ignore

        pc = Pinecone(api_key=api_key)
        try:
            index = pc.Index(index_name, host=host) if host else pc.Index(index_name)
        except TypeError:
            index = pc.Index(index_name)

        res = index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace=namespace)
        matches = getattr(res, "matches", None) or res.get("matches", [])
        return matches, None
    except ImportError:
        pass

    try:
        import pinecone  # type: ignore

        if environment:
            pinecone.init(api_key=api_key, environment=environment)
        else:
            pinecone.init(api_key=api_key)
        index = pinecone.Index(index_name)
        res = index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace=namespace)
        matches = res.get("matches", [])
        return matches, None
    except ImportError as e:
        return [], f"Pinecone client not installed ({e}). Install `pinecone` (recommended) or `pinecone-client`."


def _format_syllabus_matches(matches: List[Dict[str, Any]]) -> str:
    if not matches:
        return "No syllabus matches found in the vector database."

    lines: List[str] = []
    for i, match in enumerate(matches, start=1):
        # Pinecone SDKs may return objects or dicts.
        md = getattr(match, "metadata", None) or match.get("metadata", {}) or {}
        score = getattr(match, "score", None)
        if score is None:
            score = match.get("score")

        course_code = md.get("course_code") or md.get("code")
        course_name = md.get("course_name") or md.get("name") or md.get("title")
        header = " - ".join([p for p in [course_code, course_name] if p])

        text = (
            md.get("syllabus")
            or md.get("text")
            or md.get("chunk")
            or md.get("content")
            or md.get("page_content")
            or ""
        )
        text = str(text).strip().replace("\r\n", "\n")
        if len(text) > 1200:
            text = text[:1200].rstrip() + "…"

        source = md.get("source") or md.get("url") or md.get("doc_id") or md.get("id")
        parts = [f"{i})"]
        if score is not None:
            try:
                parts.append(f"(score={float(score):.3f})")
            except Exception:
                parts.append(f"(score={score})")
        if header:
            parts.append(header)
        if source:
            parts.append(f"[source={source}]")
        lines.append(" ".join(parts))
        if text:
            lines.append(text)
            lines.append("")

    return "\n".join(lines).strip()


@tool
def course_details(query: str) -> str:
    """
    Provide course information for course-related questions.
    
    Args:
        query: Course name, code, or related course question
        
    Returns:
        str: Course details or guidance
    """
    if not query or not query.strip():
        return "Please provide a course name, course code, or specific course question to look up details."

    cleaned_query = query.strip()

    matches, warning = _pinecone_query(cleaned_query, top_k=int(os.getenv("COURSE_SYLLABUS_TOP_K", "5")))
    if warning:
        return (
            f"Course syllabus lookup is unavailable: {warning}\n\n"
            "To enable it, set:\n"
            "- PINECONE_API_KEY\n"
            "- PINECONE_INDEX\n"
            "- (optional) PINECONE_NAMESPACE\n"
            "- (optional) PINECONE_HOST (serverless) or PINECONE_ENVIRONMENT (legacy)\n\n"
            f"User question: {cleaned_query}"
        )

    syllabus_context = _format_syllabus_matches(matches)
    return (
        "Course syllabus context (from vector DB). Use this to answer the user's question:\n\n"
        f"{syllabus_context}\n\n"
        f"User question: {cleaned_query}"
    )


def get_tools():
    """Get all available tools."""
    return [
        search_web,
        calculator,
        get_current_time,
        weather_lookup,
        course_details
    ]
