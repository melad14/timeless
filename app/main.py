"""Main FastAPI application"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.api import api_router
from app.database import ensure_indexes

# Initialize FastAPI app
app = FastAPI(
    title="Timeless - Time Capsule Backend",
    description="FastAPI backend for Timeless time capsule application",
    version="1.0.0"
)

settings = get_settings()


@app.on_event("startup")
def on_startup():
    ensure_indexes()


# Configure CORS
origins = settings.cors_origins
if "*" not in origins:
    origins.append("https://timless-front.vercel.app")
    origins.append("https://timeless-lemon.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manual OPTIONS handler for Vercel preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "ok"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        },
    )

# Include API router
app.include_router(api_router)


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Timeless Messaging Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "production" if not settings.debug else "development"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
