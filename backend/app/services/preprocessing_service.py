import os
import uuid
import cv2
import numpy as np
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, List
from fastapi import HTTPException, status
from app.core.config import settings

class PreprocessingService:
    def process_document(self, document_id: str, original_file_path: str, mime_type: str) -> Dict[str, Any]:
        """
        Processes a document for OCR.
        Does not overwrite the original file.
        Returns preprocessing metadata and paths to processed images.
        """
        path = Path(original_file_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Original document {document_id} not found."
            )
            
        processed_dir = Path(settings.PROCESSED_DIR) if hasattr(settings, 'PROCESSED_DIR') else Path("storage/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
            
        output_pages = []
        original_dims = []
        processed_dims = []

        if mime_type == "application/pdf":
            try:
                doc = fitz.open(path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    # Render to image with 300 DPI for good OCR quality
                    pix = page.get_pixmap(dpi=300)
                    img_data = pix.tobytes("png")
                    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
                    
                    if img is None:
                        continue
                        
                    original_dims.append(f"{img.shape[1]}x{img.shape[0]}")
                    processed_img = self._preprocess_image(img)
                    processed_dims.append(f"{processed_img.shape[1]}x{processed_img.shape[0]}")
                    
                    out_name = f"{document_id}_page_{page_num+1}.png"
                    out_path = processed_dir / out_name
                    cv2.imwrite(str(out_path), processed_img)
                    output_pages.append(out_name)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing PDF: {str(e)}"
                )
        else:
            img = cv2.imread(str(path))
            if img is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to load image. File may be corrupted or unsupported."
                )
                
            original_dims.append(f"{img.shape[1]}x{img.shape[0]}")
            processed_img = self._preprocess_image(img)
            processed_dims.append(f"{processed_img.shape[1]}x{processed_img.shape[0]}")
            
            out_name = f"{document_id}_page_1.png"
            out_path = processed_dir / out_name
            cv2.imwrite(str(out_path), processed_img)
            output_pages.append(out_name)

        return {
            "document_id": document_id,
            "status": "processed",
            "page_count": len(output_pages),
            "original_dimensions": original_dims,
            "processed_dimensions": processed_dims,
            "preprocessing_steps_applied": ["grayscale", "denoise", "adaptive_threshold"],
            "processed_pages": output_pages
        }

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        # Convert to Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoising: Non-local means denoising for preserving edges
        denoised = cv2.fastNlMeansDenoising(gray, h=10, searchWindowSize=21, templateWindowSize=7)
        
        # Adaptive Thresholding: Binarizes the image while handling varying illumination
        # (Useful for mobile phone pictures with shadows)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
