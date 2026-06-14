import uuid
import logging
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store trace_id per request
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract trace ID
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        # Store in request state and context var
        request.state.trace_id = trace_id
        token = trace_id_var.set(trace_id)
        
        try:
            response = await call_next(request)
            # Add trace ID to response header
            response.headers["X-Trace-ID"] = trace_id
            return response
        except Exception:
            # In case of unhandled exception, still set the header if possible
            # The exception handler will format the response
            raise
        finally:
            trace_id_var.reset(token)

# Helper function to get current trace ID
def get_trace_id() -> str:
    return trace_id_var.get() or "unknown"