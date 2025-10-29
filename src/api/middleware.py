"""
Custom middleware for the AI Investment Research Bot API.

Implements rate limiting, request logging, and security features.
"""

import time
import uuid
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute window
        self.client_requests: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 300  # Clean up every 5 minutes
        self.last_cleanup = time.time()
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier from request."""
        # Try to get user ID from token first
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from .auth import auth_service
                token = auth_header.split(" ")[1]
                token_data = auth_service.verify_token(token)
                if token_data.user_id:
                    return f"user:{token_data.user_id}"
            except Exception:
                pass
        
        # Fall back to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self):
        """Clean up old request records."""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - self.window_size
        
        for client_id in list(self.client_requests.keys()):
            requests = self.client_requests[client_id]
            
            # Remove old requests
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            # Remove empty deques
            if not requests:
                del self.client_requests[client_id]
        
        self.last_cleanup = current_time
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        requests = self.client_requests[client_id]
        
        # Remove old requests
        while requests and requests[0] < cutoff_time:
            requests.popleft()
        
        # Check if limit exceeded
        if len(requests) >= self.requests_per_minute:
            return True
        
        # Add current request
        requests.append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Clean up old records periodically
        self._cleanup_old_requests()
        
        # Check rate limit
        client_id = self._get_client_identifier(request)
        
        if self._is_rate_limited(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Process request
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/response logging middleware.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with logging."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                    "client_ip": client_ip,
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "process_time": round(process_time, 4),
                    "client_ip": client_ip,
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self' https: data:; "
                "object-src 'none'; "
                "media-src 'self'; "
                "frame-src 'none';"
            )
        }
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Cache control middleware for static assets and API responses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.cache_rules = {
            "/static/": "public, max-age=31536000",  # 1 year for static assets
            "/docs": "no-cache, no-store, must-revalidate",  # No cache for docs
            "/redoc": "no-cache, no-store, must-revalidate",
            "/openapi.json": "no-cache, no-store, must-revalidate",
            "/v1/": "no-cache, private",  # No cache for API endpoints
        }
    
    async def dispatch(self, request: Request, call_next):
        """Add cache control headers based on request path."""
        response = await call_next(request)
        
        # Determine cache policy based on path
        path = request.url.path
        cache_control = "no-cache, private"  # Default
        
        for route_prefix, policy in self.cache_rules.items():
            if path.startswith(route_prefix):
                cache_control = policy
                break
        
        response.headers["Cache-Control"] = cache_control
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Response compression middleware (simplified version).
    Note: In production, use proper compression middleware like GZipMiddleware.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with compression headers."""
        response = await call_next(request)
        
        # Add compression hint header
        if (
            "gzip" in request.headers.get("accept-encoding", "") and
            response.headers.get("content-type", "").startswith(("application/json", "text/"))
        ):
            response.headers["Content-Encoding-Hint"] = "gzip"
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Basic request validation middleware.
    """
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Request too large",
                    "message": f"Maximum request size is {self.max_request_size} bytes"
                }
            )
        
        # Validate content type for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            if not content_type.startswith(("application/json", "application/x-www-form-urlencoded", "multipart/form-data")):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "Unsupported media type",
                        "message": "Content-Type must be application/json, application/x-www-form-urlencoded, or multipart/form-data"
                    }
                )
        
        return await call_next(request)