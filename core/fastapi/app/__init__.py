from contextlib import asynccontextmanager
import traceback
import uuid
from fastapi import Request
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from ...exception.core import AbstractException
from ..app.exception_handlers import (
    abstract_exception_handler,
    exception_handler,
    request_validation_exception_handler,
    validation_exception_handler,
)
from ..response.response_class import CustomORJSONResponse
from ..loaders.router import autoload_routers
from ..middlewares.process_time_middleware import ProcessingTimeMiddleware
from ...settings import settings


def create_app(apps_dir: str = "apps", on_startup=None, on_shutdown=None):

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if on_startup:
            await on_startup()
        print("AVC CORE:: Cooking ...")
        yield
        if on_shutdown:
            await on_shutdown()
        print("AVC CORE:: Cooked !")

    app = FastAPI(lifespan=lifespan, default_response_class=CustomORJSONResponse)

    router = autoload_routers(apps_dir)

    app.include_router(router=router)

    app.add_middleware(ProcessingTimeMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AbstractException, abstract_exception_handler)
    app.add_exception_handler(401, abstract_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
    app.add_exception_handler(ValidationError, validation_exception_handler)
    try:
        from sqlalchemy.exc import StatementError, IntegrityError
        from ..app.exception_handlers import (
            statement_error_handler,
            integrity_error_handler,
        )

        app.add_exception_handler(StatementError, statement_error_handler)
        app.add_exception_handler(IntegrityError, integrity_error_handler)
    except ImportError as e:
        pass
    app.add_exception_handler(Exception, exception_handler)

    @app.get("/api/ping", summary="Ping the API", tags=["Health Check"])
    def root():
        return HTMLResponse(
            content="<html><h1>Haa shit! My Code is working.</h1></html>"
        )

    return app
