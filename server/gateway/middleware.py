"""API Gateway middleware for rate limiting, security headers, and request tracking."""
import time
import uuid
from typing import Callable, Dict, List
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple sliding window rate limiter per client IP."""
    def __init__(self, app, max_requests_per_minute: int = 120):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.request_records: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old timestamps
        records = self.request_records.get(client_ip, [])
        records = [t for t in records if now - t <= 60.0]
        self.request_records[client_ip] = records

        if len(records) >= self.max_requests:
            return Response(
                content="Rate limit exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        records.append(now)

        # Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", f"req_{uuid.uuid4().hex[:8]}")
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response
