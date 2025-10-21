from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.routes import router as api_router

app = FastAPI(
    title="PDF OCR API",
    description="API for converting PDF to text/JSON using OCR",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "PDF OCR API is running!",
        "endpoints": {
            "docs": "/docs",
            "upload": "/api/v1/upload",
            "ocr": "/api/v1/ocr/{file_id}",
            "pdf_to_json": "/api/v1/pdf-to-json/{file_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Create directories on startup
@app.on_event("startup")
async def startup_event():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)