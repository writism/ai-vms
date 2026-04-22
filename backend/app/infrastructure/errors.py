from fastapi import Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(f"{entity} not found: {entity_id}", code="NOT_FOUND")


class AuthenticationError(DomainError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(DomainError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, code="AUTHORIZATION_ERROR")


class ValidationError(DomainError):
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class ExternalServiceError(DomainError):
    def __init__(self, service: str, message: str):
        super().__init__(f"{service}: {message}", code="EXTERNAL_SERVICE_ERROR")


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_map = {
        "NOT_FOUND": 404,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "VALIDATION_ERROR": 422,
        "EXTERNAL_SERVICE_ERROR": 502,
    }
    status_code = status_map.get(exc.code, 400)
    return JSONResponse(
        status_code=status_code,
        content={"error": exc.code, "message": exc.message},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    import logging
    logging.getLogger(__name__).exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "Internal server error"},
    )
