from pydantic import BaseModel, Field
from typing import Optional

class PDFUploadResponse(BaseModel):
    file_name: str = Field(..., description="The name of the uploaded PDF file")
    message: str = Field(..., description="A message indicating the status of the upload")
    file_id: str = Field(..., description="A unique identifier for the uploaded file")

class OCRResult(BaseModel):
    success: bool
    text: Optional[str] = None
    pages: int
    processing_time: float
    error: Optional[str] = None

class PDFToJSONResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    pages: List[Dict[str, Any]] = []
    total_pages: int
    error: Optional[str] = None
