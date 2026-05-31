"""Health check API endpoints."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Employee Management System"
    }


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Employee Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }
