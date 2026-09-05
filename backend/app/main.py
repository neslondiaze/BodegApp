from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.exceptions import ApiError


def _error_body(
    codigo: str, mensaje: str, detalles=None, request_id: str | None = None
) -> dict:
    error: dict = {"codigo": codigo, "mensaje": mensaje}
    if detalles:
        error["detalles"] = detalles
    if request_id:
        error["request_id"] = request_id
    return {"error": error}


def register_exception_handlers(app: FastAPI) -> None:
    """Central error mapping (ESTANDARES §1: dominio→HTTP en un handler central).

    Every error response uses the uniform envelope of the integration
    contract §3.2: {"error": {codigo, mensaje, detalles?, request_id?}}.
    """

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.codigo, exc.mensaje, exc.detalles, exc.request_id),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        detalles = [
            {
                "campo": ".".join(str(p) for p in err.get("loc", [])),
                "problema": err.get("msg", "valor inválido"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "VALIDACION_ERROR",
                "Los datos enviados no son válidos.",
                detalles,
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Never leak internals; request_id is mandatory for 5xx (contract §3.2).
        return JSONResponse(
            status_code=500,
            content=_error_body(
                "ERROR_INTERNO",
                "Ocurrió un error inesperado. Intentá de nuevo más tarde.",
                request_id=getattr(request.state, "request_id", None),
            ),
        )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    # CORS: only declared frontend origins, never "*" (integration contract §3.4).
    if settings.cors_origins:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(app)

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    return app


app = create_app()
