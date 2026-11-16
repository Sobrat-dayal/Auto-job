"""Centralized exception handling mapping domain exceptions to structured API error responses."""

import logging
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AutonomException
from app.schemas.system import ErrorDetail, ErrorResponse

logger = logging.getLogger("autonom.errors")


def register_exception_handlers(app: FastAPI) -> None:
    """Registers standard exception handlers converting exceptions to typed ErrorResponse payloads."""

    @app.exception_handler(AutonomException)
    async def autonom_exception_handler(request: Request, exc: AutonomException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid4().hex[:8]}")
        logger.warning(f"[{req_id}] Domain exception {exc.code} on {request.url.path}: {exc.message}")

        resp = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                retryable=exc.retryable,
                details=exc.details,
            ),
            status_code=exc.status_code,
            request_id=req_id,
        )
        return JSONResponse(status_code=exc.status_code, content=resp.model_dump(mode="json"))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid4().hex[:8]}")
        logger.warning(f"[{req_id}] HTTP exception {exc.status_code} on {request.url.path}: {exc.detail}")

        resp = ErrorResponse(
            error=ErrorDetail(
                code=f"HTTP_{exc.status_code}",
                message=str(exc.detail),
                retryable=exc.status_code in (429, 502, 503, 504),
            ),
            status_code=exc.status_code,
            request_id=req_id,
        )
        return JSONResponse(status_code=exc.status_code, content=resp.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid4().hex[:8]}")
        logger.warning(f"[{req_id}] Validation error on {request.url.path}: {exc.errors()}")

        resp = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid request payload or query parameters.",
                retryable=False,
                details={"errors": [str(e) for e in exc.errors()]},
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request_id=req_id,
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=resp.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid4().hex[:8]}")
        logger.error(f"[{req_id}] Unhandled server exception on {request.url.path}: {exc}", exc_info=exc)

        resp = ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred.",
                retryable=False,
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=req_id,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=resp.model_dump(mode="json"),
        )
