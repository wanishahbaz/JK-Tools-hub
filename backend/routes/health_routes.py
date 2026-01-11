from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "JK-Tools-Hub API is running"
    }

@router.get("/version")
async def get_version():
    return {
        "version": "1.0.0",
        "name": "JK-Tools-Hub API"
    }