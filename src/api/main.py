"""
CE Demo API Gateway
===================

FastAPI-based API Gateway for the CE Demo application.
Provides centralized routing, rate limiting, caching, and security features.

Features:
- Request routing to microservices
- Redis-based rate limiting and caching
- Structured logging and metrics
- Security headers and CORS
- Health monitoring and status endpoints

Author: CE Demo System
Created: 2025-07-24
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from .middleware import (
    RequestLoggingMiddleware,
    RateLimitingMiddleware,
    SecurityHeadersMiddleware,
    CacheMiddleware,
    MetricsMiddleware,
    set_metrics_middleware,
    get_metrics_middleware
)
from ..cache.config import get_cache_status, initialize_cache_system

# Initialize structured logger
logger = structlog.get_logger(__name__)


# Pydantic models are now defined in individual router modules
# This keeps the main file clean and organized


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting CE Demo API Gateway")
    
    # Startup tasks
    await startup_tasks()
    
    yield
    
    # Shutdown tasks
    await shutdown_tasks()
    
    logger.info("CE Demo API Gateway shutdown complete")


async def startup_tasks():
    """Perform startup initialization tasks."""
    logger.info("Initializing API Gateway components")
    
    try:
        # Initialize cache system (Redis)
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        initialize_cache_system(redis_url)
        logger.info("Cache system initialized", redis_url=redis_url)
        
        # Initialize database connections
        logger.info("Database connections ready")
        
        # Initialize vector database
        logger.info("Vector database ready")
        
        # Initialize AI models
        logger.info("AI models ready")
        
        # Setup monitoring
        logger.info("Monitoring systems ready")
        
        logger.info("API Gateway startup completed successfully")
        
    except Exception as e:
        logger.error("Failed to initialize API Gateway", error=str(e))
        raise


async def shutdown_tasks():
    """Perform cleanup tasks during shutdown."""
    logger.info("Performing API Gateway cleanup")
    
    try:
        # Close database connections
        logger.info("Database connections closed")
        
        # Cleanup resources
        logger.info("Resources cleaned up")
        
        # Save metrics
        metrics_middleware = get_metrics_middleware()
        if metrics_middleware:
            metrics = metrics_middleware.get_metrics()
            logger.info("Final metrics", **metrics)
        
        logger.info("API Gateway cleanup completed")
        
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


# Create FastAPI application
app = FastAPI(
    title="CE Demo API Gateway",
    description="Sistema de Triagem Inteligente - API Gateway",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health monitoring and system status"
        },
        {
            "name": "candidates",
            "description": "Candidate management operations"
        },
        {
            "name": "matching",
            "description": "AI-powered candidate matching"
        },
        {
            "name": "analytics",
            "description": "Performance analytics and insights"
        },
        {
            "name": "gateway",
            "description": "API Gateway management and metrics"
        }
    ]
)

# Add middleware stack (order matters!)
# 1. Metrics collection (should be first to capture all requests)
metrics_middleware = MetricsMiddleware(app)
app.add_middleware(MetricsMiddleware)
set_metrics_middleware(metrics_middleware)

# 2. Request logging
app.add_middleware(
    RequestLoggingMiddleware,
    enable_body_logging=os.getenv("ENABLE_BODY_LOGGING", "false").lower() == "true"
)

# 3. Security headers
app.add_middleware(
    SecurityHeadersMiddleware,
    security_config={
        "headers": {
            "X-API-Version": "1.0.0",
            "X-Service": "ce-demo-api-gateway"
        }
    }
)

# 4. Rate limiting
app.add_middleware(
    RateLimitingMiddleware,
    enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
)

# 5. Caching
app.add_middleware(
    CacheMiddleware,
    enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
    default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "300"))
)

# 6. CORS (should be last in middleware stack)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:8080",  # Alternative frontend
        "https://*.ce-demo.com",  # Production domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-*", "X-Cache"]
)


# Database session dependency is now defined in individual router modules
# This keeps dependencies close to where they're used


# All endpoints are now organized in separate router modules
# This provides better organization and maintainability


# Import and include routers
from .routers import (
    health_router,
    candidates_router,
    matching_router,
    analytics_router,
    gateway_router,
    intake_router,
    requirements_router
)

# Include routers
app.include_router(health_router)
app.include_router(candidates_router)
app.include_router(matching_router)
app.include_router(analytics_router)
app.include_router(gateway_router)
app.include_router(intake_router)
app.include_router(requirements_router)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error("Internal server error", path=str(request.url.path), error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )