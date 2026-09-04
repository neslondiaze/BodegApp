from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Liveness probe. Kept dependency-free so it never fails on DB outages."""
    return {"status": "ok", "service": "bodegapp-backend"}
