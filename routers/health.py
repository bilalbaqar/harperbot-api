from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns a simple status response
    """
    return {"status": "ok"}
