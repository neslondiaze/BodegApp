"""Security primitives: password hashing (argon2) and JWT RS256.

Key material is loaded from the paths declared in settings (BODEGAPP_
JWT_PRIVATE_KEY_PATH / BODEGAPP_JWT_PUBLIC_KEY_PATH) — keys are never
hardcoded in source (QA criterion B9). Verification is algorithm-pinned
to RS256: alg=none and HS256 tokens are rejected by construction
(QA criterion B3, algorithm-confusion attack).
"""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import (
    RefreshExpiradoError,
    TokenExpiradoError,
    TokenInvalidoError,
)

# Token type discriminator (dual-token contract: contratante / trabajo).
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Argon2 is the primary scheme; bcrypt kept as fallback for pre-existing
# hashes (bcrypt 72-byte input truncation noted, argon2 has no such cap).
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except ValueError:
        return False


class JWTKeys:
    """RS256 key pair loaded from PEM files (secrets, never hardcoded)."""

    def __init__(self, private_key_path: str, public_key_path: str) -> None:
        self._private_pem: str | None = None
        self._public_pem: str | None = None
        self._private_key_path = private_key_path
        self._public_key_path = public_key_path

    @property
    def private_pem(self) -> str:
        if self._private_pem is None:
            self._private_pem = Path(self._private_key_path).read_text(encoding="utf-8")
        return self._private_pem

    @property
    def public_pem(self) -> str:
        if self._public_pem is None:
            self._public_pem = Path(self._public_key_path).read_text(encoding="utf-8")
        return self._public_pem


_keys: JWTKeys | None = None


def get_jwt_keys() -> JWTKeys:
    """Lazy singleton so missing key files only fail when auth is used."""
    global _keys
    if _keys is None:
        settings = get_settings()
        _keys = JWTKeys(
            private_key_path=settings.jwt_private_key_path,
            public_key_path=settings.jwt_public_key_path,
        )
    return _keys


def reset_jwt_keys() -> None:
    """Reset the cached key pair (used by tests that swap key files)."""
    global _keys
    _keys = None


def create_access_token(
    *,
    sub: str,
    tenant_id: str,
    role: str,
    token_type: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Sign a dual-model JWT with RS256.

    token_type drives capability separation (contract §1 / QA B5-B6):
    - access (trabajo): authenticates regular API calls only.
    - refresh (contratante): only valid against /auth/refresh and /auth/logout.
    """
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_minutes)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "tenant_id": tenant_id,
        "role": role,
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, get_jwt_keys().private_pem, algorithm="RS256")


def create_refresh_token(
    *, sub: str, tenant_id: str, role: str, expires_delta: timedelta | None = None
) -> tuple[str, str]:
    """Sign a refresh (contratante) token; returns (token, jti)."""
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_days)
    token = create_access_token(
        sub=sub,
        tenant_id=tenant_id,
        role=role,
        token_type=TOKEN_TYPE_REFRESH,
        expires_delta=expires_delta,
    )
    jti = jwt.decode(
        token,
        get_jwt_keys().public_pem,
        algorithms=["RS256"],
        # The token was just created; only extract the jti.
        leeway=settings.jwt_clock_leeway_seconds,
    )["jti"]
    return token, jti


def decode_token(token: str) -> dict:
    """Verify signature, expiry and expected type of a dual-model JWT.

    Algorithm is pinned to RS256 on decode — jwt.decode with a fixed
    algorithms list rejects alg=none and HS256 (QA B3). Signature
    failures (wrong key) surface as TOKEN_INVALIDO (QA B2).
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            get_jwt_keys().public_pem,
            algorithms=["RS256"],
            options={"require": ["exp", "sub", "tenant_id", "typ"]},
            leeway=settings.jwt_clock_leeway_seconds,
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiradoError() from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidoError() from exc
    return payload


def decode_token_of_type(token: str, expected_type: str) -> dict:
    """Decode and enforce the dual-token capability separation.

    An access token used where a refresh token is required (or vice
    versa) is rejected with TOKEN_INVALIDO (QA B6, contract rules T2/T3).
    Expiry maps to the token type's catalog code: TOKEN_EXPIRADO for
    access tokens, REFRESH_EXPIRADO for contractor tokens (contract T4).
    """
    try:
        payload = decode_token(token)
    except TokenExpiradoError as exc:
        if expected_type == TOKEN_TYPE_REFRESH:
            raise RefreshExpiradoError() from exc
        raise
    if payload.get("typ") != expected_type:
        raise TokenInvalidoError(
            "El tipo de token no corresponde a esta operación. Iniciá sesión de nuevo."
        )
    return payload
