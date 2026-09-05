"""Domain exceptions and the API error catalog.

Error responses follow the uniform JSON envelope from the integration
contract (INTEGRACION-BACKEND-FRONTEND.md §3.2):

    {"error": {"codigo": ..., "mensaje": ..., "detalles": [...], "request_id": ...}}

Domain code must raise subclasses of ApiError; the central handlers in
app.main map them to HTTP responses. Raw exceptions never propagate.
"""

import uuid


class ApiError(Exception):
    """Base domain error carrying an error code, message and HTTP status."""

    def __init__(self, status_code: int, codigo: str, mensaje: str) -> None:
        super().__init__(mensaje)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles: list[dict[str, str]] | None = None
        # Correlation id; 5xx handlers regenerate one if missing.
        self.request_id: str = uuid.uuid4().hex[:12]

    def with_details(self, detalles: list[dict[str, str]]) -> "ApiError":
        self.detalles = detalles
        return self


class CredencialesInvalidasError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            codigo="CREDENCIALES_INVALIDAS",
            mensaje="Usuario o contraseña incorrectos. Verificá tus datos e intentá de nuevo.",
        )


class TokenAusenteError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            codigo="TOKEN_AUSENTE",
            mensaje="Necesitás iniciar sesión para acceder a este recurso.",
        )


class TokenInvalidoError(ApiError):
    def __init__(self, mensaje: str | None = None) -> None:
        super().__init__(
            status_code=401,
            codigo="TOKEN_INVALIDO",
            mensaje=mensaje
            or "Tu sesión no es válida. Iniciá sesión de nuevo.",
        )


class TokenExpiradoError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            codigo="TOKEN_EXPIRADO",
            mensaje="Tu sesión expiró. Iniciá sesión de nuevo.",
        )


class RefreshInvalidoError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            codigo="REFRESH_INVALIDO",
            mensaje="No pudimos renovar tu sesión. Iniciá sesión de nuevo.",
        )


class RefreshExpiradoError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            codigo="REFRESH_EXPIRADO",
            mensaje="Tu sesión expiró por inactividad. Iniciá sesión de nuevo.",
        )


class PermisoInsuficienteError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            codigo="PERMISO_INSUFICIENTE",
            mensaje="No tenés permiso para realizar esta acción.",
        )


class RecursoNoEncontradoError(ApiError):
    """404 for resources that do not exist in the caller's tenant.

    The contract (§3.2) requires 404 — not 403 — for resources owned by
    another tenant, so existence is never leaked across tenants.
    """

    def __init__(self, mensaje: str | None = None) -> None:
        super().__init__(
            status_code=404,
            codigo="RECURSO_NO_ENCONTRADO",
            mensaje=mensaje or "El recurso solicitado no existe en esta tienda.",
        )
