"""API routes package."""
from src.api.routes.cds import router as cds_router
from src.api.routes.health import router as health_router

__all__ = ["cds_router", "health_router"]
