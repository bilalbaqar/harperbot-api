from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import openai
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Pydantic models for request/response validation
class Message(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of conversation messages")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's reply")

# OpenAI client will be initialized in the function to avoid startup errors

@router.post("/chat-gpt-5", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that uses OpenAI GPT-5 responses API to generate responses
    
    Args:
        request: ChatRequest containing the conversation messages
        
    Returns:
        ChatResponse with the assistant's reply
        
    Raises:
        HTTPException: For validation or API errors
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY environment variable is not set. Please set it in your .env file or environment."
            )
        
        client = OpenAI(api_key=api_key)
        
        # Validate that we have at least one message
        if not request.messages:
            raise HTTPException(status_code=400, detail="At least one message is required")
        
        # Get the last user message as input for GPT-5 responses API
        # The responses API takes a single input string, not a conversation history
        user_messages = [msg.content for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="At least one user message is required")
        
        # Use the last user message as input
        user_input = user_messages[-1]
        
        try:
            # Try GPT-5 responses API first
            response = client.responses.create(
                model="gpt-5",
                input=user_input,
                reasoning={
                    "effort": "minimal"
                }
            )
            
            # Extract the response - GPT-5 responses API returns the answer directly
            assistant_reply = response.answer
            
        except Exception as gpt5_error:
            # Fallback to GPT-4 chat completions if GPT-5 responses API is not available
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": user_input}],
                    temperature=0.2,
                    max_tokens=1000,
                )
                
                assistant_reply = response.choices[0].message.content
                
            except Exception as fallback_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Both GPT-5 responses API and GPT-4 fallback failed. GPT-5 error: {str(gpt5_error)}, Fallback error: {str(fallback_error)}"
                )
        
        return ChatResponse(response=assistant_reply)
        
    except openai.AuthenticationError:
        raise HTTPException(
            status_code=401, 
            detail="OpenAI API authentication failed. Please check your API key."
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=429, 
            detail="OpenAI API rate limit exceeded. Please try again later."
        )
    except openai.APIError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"OpenAI API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )
