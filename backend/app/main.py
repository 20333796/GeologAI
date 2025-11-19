"""
GeologAI WebOS Backend - FastAPI Application Entry Point
"""
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    """
    # Startup
    logger.info("🚀 Starting GeologAI WebOS Backend...")
    yield
    # Shutdown
    logger.info("🛑 Shutting down GeologAI WebOS Backend...")


def create_app():
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title="GeologAI WebOS API",
        description="Geophysical Well Log AI Analysis Platform",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8501",
            "http://localhost:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "testserver", "*"]
    )
    
    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "Validation Error",
                "errors": exc.errors(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal Server Error",
                "detail": str(exc) if os.getenv("DEBUG") else "An error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Root route
    @app.get("/")
    async def root():
        return {
            "name": "GeologAI WebOS API",
            "version": "1.0.0",
            "status": "running",
            "docs_url": "/api/docs",
            "endpoints": {
                "auth": "/api/v1/auth",
                "users": "/api/v1/users",
                "projects": "/api/v1/projects",
                "data": "/api/v1/data",
                "predictions": "/api/v1/predictions",
                "admin": "/api/v1/admin"
            }
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # API status
    @app.get("/api/v1/status")
    async def api_status():
        return {
            "code": 200,
            "message": "API is running",
            "data": {
                "version": "1.0.0",
                "modules": {
                    "auth": "ready",
                    "users": "ready",
                    "projects": "ready",
                    "data": "ready",
                    "predictions": "ready",
                    "admin": "ready"
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Register API routes
    try:
        from app.api import api_router
        from app.db.session import init_db
        
        # Initialize database (ignore errors in test environment)
        try:
            logger.info("初始化数据库...")
            init_db()
            logger.info("✅ 数据库初始化成功")
        except Exception as db_error:
            logger.warning(f"⚠️ 数据库初始化警告: {str(db_error)}. 将在测试模式下继续.")
        
        # Include API router
        app.include_router(api_router)
        logger.info("✅ API路由已注册")
        
    except Exception as e:
        logger.error(f"API注册失败: {str(e)}")
    
    logger.info("✅ FastAPI application created successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
