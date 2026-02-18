# app/exceptions/handlers.py
from fastapi import FastAPI, Request, JSONResponse
from .exceptions import ServiceError


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(ServiceError)
    async def handle_service_error(request: Request, exc: ServiceError):
        return JSONResponse(
            content=exc.message,
            status_code=exc.status_code
        )
