import os

import uvicorn
from fastapi import FastAPI, Request

from clap_ops_service.api.v1.routes import v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")


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