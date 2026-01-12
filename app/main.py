from fastapi import FastAPI

from app.api.v1 import letters


app = FastAPI(
    title="PDF Letter Service",
    description="Microservice for generating formal PDF letters",
    version="0.1.0"
)

# Include v1 API routers
app.include_router(letters.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "PDF Letter Service is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
