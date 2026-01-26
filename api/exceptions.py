"""
Custom exceptions for PersonalAxis API.

These exceptions map to specific error codes defined in phase_6_plan.md
and provide structured error responses to clients.
"""

from typing import Optional, Dict, Any


class PersonalAxisException(Exception):
    """Base exception for all PersonalAxis API errors."""
    
    def __init__(
        self,
        code: str,
        message: str,
        user_message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.user_message = user_message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


# ============================================================================
# Authentication Errors (403)
# ============================================================================

class AuthMissingError(PersonalAxisException):
    """Raised when authentication is missing."""
    
    def __init__(self):
        super().__init__(
            code="AUTH_MISSING",
            message="Authentication token is missing",
            user_message="Kimlik doğrulama bilgisi eksik.",
            status_code=403
        )


class AuthInvalidError(PersonalAxisException):
    """Raised when credentials are incorrect."""
    
    def __init__(self):
        super().__init__(
            code="AUTH_INVALID",
            message="Provided credentials are incorrect",
            user_message="Kimlik doğrulama başarısız.",
            status_code=403
        )


class AuthSessionExpiredError(PersonalAxisException):
    """Raised when session is missing or expired."""

    def __init__(self):
        super().__init__(
            code="AUTH_EXPIRED",
            message="Session is missing or expired",
            user_message="Oturum süresi doldu. Lütfen tekrar giriş yapın.",
            status_code=401
        )


# ============================================================================
# Notion API Errors
# ============================================================================

class NotionAuthError(PersonalAxisException):
    """Raised when Notion token is invalid or integration has no access."""
    
    def __init__(self, original_message: str = ""):
        super().__init__(
            code="NOTION_AUTH_FAILED",
            message=f"Notion authentication failed: {original_message}",
            user_message="Notion bağlantısı yetkilendirilemedi. Lütfen daha sonra tekrar deneyin.",
            status_code=401,
            details={"original_error": original_message}
        )


class NotionRateLimitError(PersonalAxisException):
    """Raised when Notion API rate limit is exceeded."""
    
    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            code="NOTION_RATE_LIMIT",
            message="Notion API rate limit exceeded",
            user_message="Çok fazla istek gönderildi. Lütfen birkaç saniye bekleyin.",
            status_code=429,
            details={"retry_after": retry_after or 60}
        )


class NotionAPIError(PersonalAxisException):
    """Generic Notion API error."""
    
    def __init__(self, status_code: int = 500, original_message: str = ""):
        super().__init__(
            code="NOTION_API_ERROR",
            message=f"Notion API error (status {status_code}): {original_message}",
            user_message="Notion ile iletişimde bir sorun oluştu. Lütfen daha sonra tekrar deneyin.",
            status_code=502,
            details={"notion_status": status_code, "original_error": original_message}
        )


class NotionResourceNotFoundError(PersonalAxisException):
    """Raised when a Notion database or page is not found."""
    
    def __init__(self, resource_type: str = "resource", resource_name: str = ""):
        super().__init__(
            code="NOTION_RESOURCE_NOT_FOUND",
            message=f"Notion {resource_type} not found: {resource_name}",
            user_message=f"İstenen {resource_type} bulunamadı.",
            status_code=404,
            details={"resource_type": resource_type, "resource_name": resource_name}
        )


class NotionTimeoutError(PersonalAxisException):
    """Raised when Notion API request times out."""
    
    def __init__(self):
        super().__init__(
            code="NOTION_TIMEOUT",
            message="Connection to Notion API timed out",
            user_message="Notion bağlantısı zaman aşımına uğradı. Lütfen tekrar deneyin.",
            status_code=504
        )


# ============================================================================
# Validation Errors (422)
# ============================================================================

class InvalidReviewTypeError(PersonalAxisException):
    """Raised when review type is not supported."""
    
    def __init__(self, provided_type: str):
        super().__init__(
            code="INVALID_REVIEW_TYPE",
            message=f"Invalid review type: {provided_type}",
            user_message=f"Geçersiz değerlendirme türü: {provided_type}. Geçerli türler: weekly, monthly, quarterly, yearly.",
            status_code=422,
            details={"provided": provided_type, "valid_types": ["weekly", "monthly", "quarterly", "yearly"]}
        )


class InvalidPeriodFormatError(PersonalAxisException):
    """Raised when period format is malformed."""
    
    def __init__(self, provided_period: str, expected_format: str = ""):
        super().__init__(
            code="INVALID_PERIOD_FORMAT",
            message=f"Invalid period format: {provided_period}",
            user_message=f"Geçersiz dönem formatı. Beklenen: {expected_format}",
            status_code=422,
            details={"provided": provided_period, "expected_format": expected_format}
        )
