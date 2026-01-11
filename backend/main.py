import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="JK-Tools-Hub API",
    description="Advanced Media Tools Web App Backend",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from routes import image_routes, health_routes

# Include routers
app.include_router(health_routes.router, prefix="/api", tags=["Health"])
app.include_router(image_routes.router, prefix="/api", tags=["Image Tools"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to JK-Tools-Hub API",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)