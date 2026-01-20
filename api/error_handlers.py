"""
Generic error handling utilities for API routes.

This module provides a decorator that automatically handles Notion API errors
and other common exceptions, reducing code duplication across routers.
"""

from functools import wraps
from notion_client.errors import APIResponseError, APIErrorCode
from api.exceptions import (
    NotionAuthError,
    NotionRateLimitError,
    NotionAPIError,
    NotionTimeoutError,
    NotionResourceNotFoundError
)
import requests


def handle_notion_errors(func):
    """
    Decorator that automatically handles Notion API errors for route handlers.
    
    This decorator wraps async route functions and catches:
    - APIResponseError: Maps to specific NotionError exceptions
    - requests.exceptions.Timeout: Maps to NotionTimeoutError
    - Other exceptions: Re-raised for global handler
    
    Usage:
        @router.get("/example")
        @handle_notion_errors
        async def my_route():
            # Your code here
            pass
    
    Returns:
        Decorated async function with error handling.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except APIResponseError as e:
            # Handle Notion API errors with specific error codes
            if e.code == APIErrorCode.Unauthorized:
                raise NotionAuthError(str(e))
            elif e.code == APIErrorCode.RestrictedResource:
                raise NotionAuthError(str(e))
            elif e.code == APIErrorCode.ObjectNotFound:
                raise NotionResourceNotFoundError(
                    resource_type="Notion object",
                    resource_name="requested resource"
                )
            elif e.code == APIErrorCode.RateLimited:
                raise NotionRateLimitError()
            elif e.code == APIErrorCode.ServiceUnavailable:
                raise NotionAPIError(503, str(e))
            elif e.code == APIErrorCode.ConflictError:
                raise NotionAPIError(409, str(e))
            elif e.code in [
                APIErrorCode.InvalidJSON,
                APIErrorCode.InvalidRequestURL,
                APIErrorCode.InvalidRequest,
                APIErrorCode.ValidationError
            ]:
                raise NotionAPIError(400, str(e))
            else:
                raise NotionAPIError(e.status, str(e))
        except requests.exceptions.Timeout:
            # Handle connection timeouts
            raise NotionTimeoutError()
        except Exception:
            # Re-raise other exceptions for global handler
            raise
    
    return wrapper
