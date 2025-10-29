"""
FastAPI backend services for AI Investment Research Bot.

This package contains all API-related modules including:
- Authentication and authorization
- REST API endpoints
- WebSocket handlers
- Middleware and security
- Business logic integration
"""

from .app import create_app
from .auth import get_current_user, create_access_token
from .dependencies import get_db, get_current_active_user

__all__ = [
    "create_app",
    "get_current_user", 
    "create_access_token",
    "get_db",
    "get_current_active_user"
]