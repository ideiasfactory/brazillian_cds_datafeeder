"""FastAPI application for Brazilian CDS data."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from src.api.routes import cds_router, health_router, home_router, favicon_router
from src.utils import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(favicon_router)  # Favicon must be early for browser requests
app.include_router(home_router)  # Home page must be first for root route
app.include_router(health_router)
app.include_router(cds_router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    from src.utils import get_logger
    logger = get_logger()
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    from src.utils import get_logger
    logger = get_logger()
    logger.info("Shutting down API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
