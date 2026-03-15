import logging
import sys
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from secure import Secure
from app.core.config import settings
from app.core.database import Base, engine
# Import models before creating the app so they register with Base.metadata
from app.models import User, Chat, Message
from app.api import auth, chats, messages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("Imports completed successfully")

# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.2,
        environment="production" if not settings.DEBUG else "development",
    )
    logger.info("✓ Sentry error tracking initialized")
else:
    logger.info("Sentry DSN not configured, skipping error tracking")

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-time AI chat platform powered by Claude API. Stream conversations, manage multiple chats, and leverage advanced language models.",
    contact={
        "name": "Vladyslav Maidaniuk",
        "email": "vla.maidaniuk@gmail.com",
    },
    openapi_tags=[
        {"name": "auth", "description": "Authentication — register, login, token refresh"},
        {"name": "chats", "description": "Chat sessions CRUD"},
        {"name": "messages", "description": "Messages and Claude AI streaming"},
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
secure_headers = Secure()


@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response


# Application startup
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    from app.core.cache import init_cache

    logger.info("=" * 50)
    logger.info("FastAPI application STARTING")
    logger.info(f"Project: {settings.PROJECT_NAME}")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"API Base: {settings.API_V1_STR}")

    try:
        logger.info("Testing database connection...")
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection SUCCESSFUL")
    except Exception as e:
        logger.error(f"✗ Database connection FAILED: {str(e)}")
        # Continue anyway - migrations might fix the connection

    # Initialize cache (ignore errors if Redis unavailable)
    try:
        await init_cache()
    except Exception as e:
        logger.warning(f"Cache initialization failed: {str(e)}")

    logger.info("FastAPI application READY to handle requests")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    logger.info("Shutting down application...")
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(chats.router, prefix=settings.API_V1_STR)
app.include_router(messages.router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "unknown"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check - DB connection failed: {str(e)}")
        db_status = "disconnected"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "version": settings.VERSION,
        "database": db_status,
        "api": settings.API_V1_STR,
    }


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "api": settings.API_V1_STR,
        "docs": "/docs",
        "status": "running",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler to log all unhandled exceptions"""
    error_msg = str(exc)
    logger.error(
        f"Unhandled {type(exc).__name__} at {request.url.path}: {error_msg}",
        exc_info=True,
        extra={"method": request.method}
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": error_msg if settings.DEBUG else "An error occurred",
            "type": type(exc).__name__ if settings.DEBUG else None,
        }
    )
