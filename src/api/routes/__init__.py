"""API routes package."""
from src.api.routes.cds import router as cds_router
from src.api.routes.health import router as health_router
from src.api.routes.home import router as home_router

__all__ = ["cds_router", "health_router", "home_router"]
