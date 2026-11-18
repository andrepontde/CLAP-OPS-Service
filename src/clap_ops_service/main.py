import logging
import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from clap_ops_service.api.v1.routes import v1_router
from clap_ops_service.services.exceptions import DatabaseOperationError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("clap_ops")

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

# TODO - move logging and exception handling to middleware later on, this is just
# a temporary solution to get the service running and logging properly
@app.exception_handler(DatabaseOperationError)
async def database_operation_handler(
    request: Request,
    error: DatabaseOperationError,
) -> JSONResponse:
    logger.exception("Database operation failed")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred"},
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.url.path.startswith("/api/v1/auth/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def main() -> None:
    uvicorn.run(
        "clap_ops_service.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )