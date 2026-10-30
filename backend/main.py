from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes.scripts import router as scripts_router

app = FastAPI(
    title="AI-Powered Podcast & YouTube Script Planner API",
    version="1.0.0"
)

# Proper CORS configuration for local React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scripts_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Script Planner API",
        "model": settings.GEMINI_MODEL,
        "has_api_key": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_actual_gemini_api_key_here")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    