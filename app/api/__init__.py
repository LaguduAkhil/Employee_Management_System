"""API routes for the application."""

from app.api import auth, employees, departments, leaves, attendance, health

__all__ = ["auth", "employees", "departments", "leaves", "attendance", "health"]
