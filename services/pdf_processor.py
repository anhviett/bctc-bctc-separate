import pdf2image
import pytesseract
import json
import time
import os 
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
from PIL import Image

class PDFProcessor:
    def ___init__(self):
        self.supported_languages = ['vie', 'eng'];

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Tiền xử lý ảnh để cải thiện OCR accuracy"""
        img = np.array(image)
        
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(thresh)
        return processed_image
    
    def pdf_to_text(self, pdf_path: str, language: str = 'vie') -> Dict[str, Any]:
        """ Chuyển đổi PDF sang text sử dụng OCR"""
        start_time = time.time()

        try:
            images = pdf2image.convert_from_path(pdf_path, dpi=300)

            all_text = ""
            page_results = []

            for i, image in enumerate(images):
                # Preprocess the image
                processed_image = self.preprocess_image(image)

                # config OCR vietnamese
                custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                text = pytesseract.image_to_string(
                    processed_image, 
                    lang=language, 
                    config=custom_config
                )
                
                all_text += f"=== Page {i+1} ===\n{text}\n\n"
                page_results.append({
                    "page_number": i + 1,
                    "text": text.strip(),
                    "char_count": len(text.strip())
                })
            
            processing_time = time.time() - start_time

            return {
                "success": True,
                "text": all_text,
                "pages": page_results,
                "total_pages": len(images),
                "processing_time": round(processing_time, 2)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    def pdf_to_json(self, pdf_path: str, language: str = 'vie')->Dict[str, Any]:
        """Convert PDF to structured JSON"""
        ocr_result = self.pdf_to_text(pdf_path, language)

        if not ocr_result["success"]:
            return ocr_result
        
        # Structure the data into JSON output
        structured_data = {
            "metadata": {
                "total_pages": ocr_result["total_pages"],
                "processing_time": ocr_result["processing_time"],
                "language": language,
                "file_size": os.path.getsize(pdf_path)
            },
            "content": {
                "full_text": ocr_result["text"],
                "pages": ocr_result["pages"]
            },
            "summary": {
                "total_characters": sum(page["char_count"] for page in ocr_result["pages"]),
                "average_chars_per_page": sum(page["char_count"] for page in ocr_result["pages"]) / ocr_result["total_pages"]
            }
        }

        return {
            "success": True,
            "data": structured_data,
            "pages": ocr_result["pages"],
            "total_pages": ocr_result["total_pages"]
        }

# Global instance
pdf_processor = PDFProcessor()