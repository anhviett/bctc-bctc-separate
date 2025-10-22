from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import aiofiles
from typing import Optional

from app.services.pdf_processor import pdf_processor
from app.models.schemas import PDFUploadResponse, OCRResult, PDFToJSONResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    # Save uploaded file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return PDFUploadResponse(
        file_name=file.filename,
        message="File uploaded successfully",
        file_id=file_id
    )

@router.post("/ocr/{file_id}", response_model=OCRResult)
async def ocr_pdf(
    file_id: str,
    language: str = Query('vie', description="OCR language (vie, eng)")
):
    """Perform OCR on uploaded PDF"""
    clean_id = os.path.basename(file_id.strip().replace("'", "").replace('"', ""))
    file_path = os.path.join(UPLOAD_DIR, f"{clean_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    result = pdf_processor.pdf_to_text(file_path, language)
    print("OCR result raw:", result)

    if isinstance(result, dict) and isinstance(result.get("pages"), list):
        all_text = "\n".join([p.get("text", "") for p in result["pages"]])
        page_count = len(result["pages"])
        result = {
            "success": True,
            "text": all_text,
            "pages": page_count,
            "processing_time": result.get("processing_time", 0.0),
            "error": None
        }

    return OCRResult(**result)

@router.post("/pdf-to-json/{file_id}", response_model=PDFToJSONResponse)
async def pdf_to_json(
    file_id: str,
    language: str = Query('vie', description="OCR language (vie, eng)")
):
    """Convert PDF to JSON with OCR"""
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    result = pdf_processor.pdf_to_json(file_path, language)
    
    # Save JSON result
    if result["success"]:
        output_path = os.path.join(OUTPUT_DIR, f"{file_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    return PDFToJSONResponse(**result)

@router.get("/download-json/{file_id}")
async def download_json(file_id: str):
    """Download JSON result"""
    file_path = os.path.join(OUTPUT_DIR, f"{file_id}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "JSON file not found")
    
    return FileResponse(
        file_path,
        media_type='application/json',
        filename=f"result_{file_id}.json"
    )

@router.get("/languages")
async def get_supported_languages():
    """Get supported OCR languages"""
    return {
        "supported_languages": pdf_processor.supported_languages,
        "default": "vie"
    }