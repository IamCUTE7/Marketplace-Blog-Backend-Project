from fastapi import FastAPI

app = FastAPI(title="Marketplace Blog API")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
