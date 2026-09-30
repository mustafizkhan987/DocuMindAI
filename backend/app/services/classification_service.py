import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.classification import ClassificationResult, DocumentType

class RuleBasedClassifier:
    """
    A lightweight, explainable rule-based document classifier.
    Designed to be easily replaceable with an ML-based implementation in the future.
    """
    def __init__(self):
        # Define signal dictionaries with associated weights
        self.category_signals = {
            DocumentType.INVOICE: {
                "tax invoice": 3.0,
                "invoice": 2.0,
                "gstin": 2.0,
                "cgst": 1.5,
                "sgst": 1.5,
                "igst": 1.5,
                "invoice no": 1.0,
                "taxable value": 1.0,
                "hsn": 1.0,
            },
            DocumentType.RECEIPT: {
                "receipt": 2.0,
                "paid": 1.5,
                "payment received": 2.0,
                "transaction id": 1.0,
                "amount paid": 1.5,
                "cash memo": 1.5,
            },
            DocumentType.PURCHASE_ORDER: {
                "purchase order": 3.0,
                "po number": 2.0,
                "po date": 2.0,
                "supplier": 1.0,
                "ordered quantity": 1.0,
                "delivery date": 1.0,
            },
            DocumentType.BILL: {
                "bill": 1.5,
                "amount due": 1.5,
                "due date": 1.0,
                "billing": 1.0,
                "statement": 1.0,
                "electricity": 1.0,
                "water bill": 1.5,
            }
        }
        
    def _normalize_text(self, text: str) -> str:
        """
        Normalizes OCR text to lower case and single spacing for consistent matching.
        """
        text = text.lower()
        # Replace punctuation that might interfere with exact phrase matching
        text = re.sub(r'[^\w\s]', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def classify(self, document_id: str, text: str) -> ClassificationResult:
        if not text.strip():
            return ClassificationResult(
                document_id=document_id,
                document_type=DocumentType.OTHER,
                confidence=0.0,
                signals=["empty_text"]
            )
            
        normalized_text = self._normalize_text(text)
        
        scores: Dict[DocumentType, float] = {doc_type: 0.0 for doc_type in DocumentType if doc_type != DocumentType.OTHER}
        matched_signals_per_type: Dict[DocumentType, List[str]] = {doc_type: [] for doc_type in DocumentType if doc_type != DocumentType.OTHER}
        
        # Calculate scores
        for doc_type, signals in self.category_signals.items():
            for signal, weight in signals.items():
                if signal in normalized_text:
                    scores[doc_type] += weight
                    matched_signals_per_type[doc_type].append(signal)
        
        # Find the highest scoring category
        best_type = DocumentType.OTHER
        best_score = 0.0
        
        for doc_type, score in scores.items():
            if score > best_score:
                best_score = score
                best_type = doc_type
                
        # Handle conflicts/ambiguity (e.g. if two classes have the same high score)
        # Simple thresholding for OTHER
        threshold = 2.0
        
        if best_score < threshold:
            return ClassificationResult(
                document_id=document_id,
                document_type=DocumentType.OTHER,
                confidence=1.0 if best_score == 0 else round(best_score / (threshold * 2), 2),
                signals=["no_strong_signals_found"]
            )
            
        # Confidence logic: capping the score to a normalized 0.0-1.0 range.
        # A score of 5.0+ represents 99% confidence.
        # This is a heuristic probability, not a statistical one.
        raw_confidence = best_score / 6.0 
        confidence = min(0.99, max(0.50, raw_confidence))
        
        return ClassificationResult(
            document_id=document_id,
            document_type=best_type,
            confidence=round(confidence, 4),
            signals=matched_signals_per_type[best_type]
        )


class ClassificationService:
    def __init__(self):
        self.classifier = RuleBasedClassifier()
        
    def classify_document(self, document_id: str) -> ClassificationResult:
        # Load OCR results
        ocr_dir = Path(settings.STORAGE_DIR) / "ocr_results" if hasattr(settings, 'STORAGE_DIR') else Path("storage/ocr_results")
        result_file = ocr_dir / f"{document_id}.json"
        
        if not result_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="OCR text not found for this document. Please run OCR pipeline first."
            )
            
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                ocr_data = json.load(f)
                text = ocr_data.get("text", "")
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Corrupted OCR result file."
            )
            
        return self.classifier.classify(document_id, text)

classification_service = ClassificationService()
