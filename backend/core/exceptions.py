"""Centralized FastAPI exception handling."""

from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.logger import logger
from backend.core.responses import build_response


class TalentSyncError(Exception):
    status_code = 500
    message = "Internal server error"

    def __init__(self, message: str | None = None, status_code: int | None = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class FileUploadError(TalentSyncError):
    status_code = 400
    message = "File upload failed"


class MissingResourceError(TalentSyncError):
    status_code = 404
    message = "Required resource was not found"


def _request_start(request: Request) -> float:
    return getattr(request.state, "start_time", perf_counter())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TalentSyncError)
    async def talentsync_exception_handler(request: Request, exc: TalentSyncError):
        logger.warning(
            "handled_error path=%s status=%s message=%s",
            request.url.path,
            exc.status_code,
            exc.message,
        )
        response = build_response(
            success=False,
            message=exc.message,
            data=None,
            start_time=_request_start(request),
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "http_error path=%s status=%s detail=%s",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        response = build_response(
            success=False,
            message=str(exc.detail),
            data=None,
            start_time=_request_start(request),
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("validation_error path=%s errors=%s", request.url.path, exc.errors())
        response = build_response(
            success=False,
            message="Request validation failed",
            data={"errors": exc.errors()},
            start_time=_request_start(request),
        )
        return JSONResponse(status_code=422, content=response.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_error path=%s", request.url.path)
        response = build_response(
            success=False,
            message="Internal server error",
            data=None,
            start_time=_request_start(request),
        )
        return JSONResponse(status_code=500, content=response.model_dump(mode="json"))
