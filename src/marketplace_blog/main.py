from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from marketplace_blog.api.router import api_router
from marketplace_blog.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    start_time = perf_counter()

    response = await call_next(request)

    process_time = perf_counter() - start_time

    print(f"{request.method} {request.url.path}" f"took {process_time:.4f}s")

    response.headers["X-Process-Time"] = str(process_time)

    return response
