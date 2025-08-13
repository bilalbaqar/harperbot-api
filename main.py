from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, chat

app = FastAPI(
    title="HarperBot API",
    description="API for HarperBot application",
    version="1.0.0"
)

# Add CORS middleware with permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(chat.router, tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
