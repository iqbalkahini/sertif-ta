from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from brotli_asgi import BrotliMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="Sistem Surat Menyurat API",
    description="API for generating official dynamic letters (Surat Dinas, Surat Tugas, etc.)",
    version="1.0.0"
)

# Brotli compression for faster response delivery
app.add_middleware(BrotliMiddleware, minimum_size=500, gzip_fallback=True)

# Mount static files for logos/assets if needed
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Service is running. Documentation at /docs"}
