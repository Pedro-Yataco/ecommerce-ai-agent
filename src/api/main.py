from fastapi import FastAPI

app = FastAPI(
    title="Ecommerce AI Agent API",
    version="0.1.0",
    description="API for the ecommerce AI agent MVP.",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}