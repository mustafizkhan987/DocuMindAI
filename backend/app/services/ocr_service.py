import os
import re
from pathlib import Path
from typing import List, Optional
import json
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.ocr import OCRDocumentResult, OCRPageResult

try:
    import easyocr
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False

class OCRService:
    def __init__(self):
        self._reader = None

    @property
    def ocr_engine(self):
        if not self._reader:
            if not _OCR_AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="EasyOCR is not available in the current environment."
                )
            # Initialize EasyOCR
            # lang_list=['en'] as a baseline.
            self._reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        return self._reader

    def extract_text(self, document_id: str) -> OCRDocumentResult:
        processed_dir = Path(settings.PROCESSED_DIR) if hasattr(settings, 'PROCESSED_DIR') else Path("storage/processed")
        
        if not processed_dir.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processed storage not found.")
            
        page_files = list(processed_dir.glob(f"{document_id}_page_*.png"))
        
        if not page_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No processed pages found for document {document_id}. Ensure preprocessing was completed."
            )
            
        # Sort pages numerically
        page_files.sort(key=lambda p: self._extract_page_number(p.name))
        
        pages_result = []
        combined_text = []
        
        engine = self.ocr_engine
        
        for file_path in page_files:
            page_num = self._extract_page_number(file_path.name)
            
            try:
                # result is a list of (bbox, text, prob)
                result = engine.readtext(str(file_path))
                
                page_text_lines = []
                confidences = []
                
                if result:
                    for line in result:
                        if len(line) == 3:
                            _, text, conf = line
                            page_text_lines.append(text)
                            confidences.append(float(conf))
                            
                page_text = "\n".join(page_text_lines)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                pages_result.append(
                    OCRPageResult(
                        page_number=page_num,
                        text=page_text,
                        confidence=round(avg_confidence, 4) if confidences else None
                    )
                )
                
                combined_text.append(page_text)
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OCR processing failed on page {page_num}: {str(e)}"
                )
                
        result_obj = OCRDocumentResult(
            document_id=document_id,
            page_count=len(pages_result),
            text="\n\n".join(combined_text),
            pages=pages_result
        )
        
        # Save to file for subsequent pipeline stages
        ocr_dir = Path(settings.STORAGE_DIR) / "ocr_results" if hasattr(settings, 'STORAGE_DIR') else Path("storage/ocr_results")
        ocr_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = ocr_dir / f"{document_id}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(result_obj.model_dump_json(indent=2))
            
        return result_obj

    def _extract_page_number(self, filename: str) -> int:
        match = re.search(r'_page_(\d+)\.png', filename)
        if match:
            return int(match.group(1))
        return 0

ocr_service = OCRService()
