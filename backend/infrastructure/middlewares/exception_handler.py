from fastapi import Request
from fastapi.responses import JSONResponse
from features.common.types.exceptions import BaseSawtException

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, BaseSawtException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
    )
