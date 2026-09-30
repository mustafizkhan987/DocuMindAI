import re
import json
from pathlib import Path
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.invoice import InvoiceExtractionResult, CanonicalInvoice, Party, Financials
from app.services.classification_service import classification_service
from app.schemas.classification import DocumentType

class ExtractionService:
    def __init__(self):
        pass
        
    @property
    def storage_dir(self):
        return Path(settings.STORAGE_DIR) if hasattr(settings, 'STORAGE_DIR') else Path("storage")
        
    @property
    def extraction_dir(self):
        d = self.storage_dir / "extraction_results"
        d.mkdir(parents=True, exist_ok=True)
        return d
        
    def extract_invoice(self, document_id: str) -> InvoiceExtractionResult:
        if not document_id or "/" in document_id or "\\" in document_id or ".." in document_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID format."
            )

        # 1. Check if classification exists and is INVOICE.
        # We invoke classify_document which automatically checks for OCR result
        try:
            classification_result = classification_service.classify_document(document_id)
        except HTTPException as e:
            # This bubbles up 404 if OCR result doesn't exist
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Classification failed: {str(e)}"
            )

        if classification_result.document_type != DocumentType.INVOICE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice extraction is only available for documents classified as Invoice."
            )

        # 2. Read OCR Result
        ocr_result_file = self.storage_dir / "ocr_results" / f"{document_id}.json"
        if not ocr_result_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OCR text not found for this document."
            )
            
        with open(ocr_result_file, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
            text = ocr_data.get("text", "")
            
        # 3. Extract Invoice Data
        extracted_data = self._perform_extraction(text)
        
        seller = Party(
            name=extracted_data.get('seller_name'),
            gstin=extracted_data.get('seller_gstin'),
            address=extracted_data.get('seller_address')
        )
        
        buyer = Party(
            name=extracted_data.get('buyer_name'),
            gstin=extracted_data.get('buyer_gstin'),
            address=extracted_data.get('buyer_address')
        )
        
        financials = Financials(
            taxable_amount=extracted_data.get('taxable_amount'),
            cgst=extracted_data.get('cgst'),
            sgst=extracted_data.get('sgst'),
            igst=extracted_data.get('igst'),
            total_tax=extracted_data.get('total_tax'),
            grand_total=extracted_data.get('grand_total')
        )
        
        result = CanonicalInvoice(
            document_id=document_id,
            invoice_number=extracted_data.get('invoice_number'),
            invoice_date=extracted_data.get('invoice_date'),
            seller=seller,
            buyer=buyer,
            financials=financials
        )
        
        # 4. Save to local storage
        save_path = self.extraction_dir / f"{document_id}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
            
        return result

    def _perform_extraction(self, text: str) -> dict:
        data = {}
        
        from decimal import Decimal, InvalidOperation
        
        def parse_amount(val_str: str) -> Decimal:
            clean = re.sub(r'[^\d.]', '', val_str)
            try:
                return Decimal(clean)
            except (ValueError, InvalidOperation):
                return None

        # Invoice Number
        inv_no_match = re.search(r'(?i)(?:invoice\s*no|invoice\s*number|bill\s*no|bill\s*number)\s*[:\-#]?\s*([A-Z0-9\-_]+)', text)
        if inv_no_match:
            data['invoice_number'] = inv_no_match.group(1).strip()
            
        # Invoice Date
        date_match = re.search(r'\b(\d{2}[/\-\.]\d{2}[/\-\.]\d{4}|\d{4}[/\-\.]\d{2}[/\-\.]\d{2})\b', text)
        if date_match:
            data['invoice_date'] = date_match.group(1).strip()
            
        # GSTIN parsing
        # Matches exactly 15 chars following GSTIN structure
        gstin_pattern = r'\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})\b'
        gstins = list(dict.fromkeys(re.findall(gstin_pattern, text.upper())))
        if gstins:
            data['seller_gstin'] = gstins[0]
            if len(gstins) > 1:
                data['buyer_gstin'] = gstins[1]
                
        # Monetary amounts
        # Taxable Amount
        taxable_match = re.search(r'(?i)(?:taxable\s*amount|taxable\s*value)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([\d,]+\.\d{2})', text)
        if taxable_match:
            data['taxable_amount'] = parse_amount(taxable_match.group(1))
            
        # CGST
        cgst_match = re.search(r'(?i)cgst\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([\d,]+\.\d{2})', text)
        if cgst_match:
            data['cgst'] = parse_amount(cgst_match.group(1))
            
        # SGST
        sgst_match = re.search(r'(?i)sgst\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([\d,]+\.\d{2})', text)
        if sgst_match:
            data['sgst'] = parse_amount(sgst_match.group(1))
            
        # IGST
        igst_match = re.search(r'(?i)igst\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([\d,]+\.\d{2})', text)
        if igst_match:
            data['igst'] = parse_amount(igst_match.group(1))
            
        # Grand Total
        total_match = re.search(r'(?i)(?:grand\s*total|total|net\s*amount|amount\s*payable)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([\d,]+\.\d{2})', text)
        if total_match:
            data['grand_total'] = parse_amount(total_match.group(1))
            
        # Basic Buyer / Seller name heuristics
        # Typically the first line is the Seller name. 
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            data['seller_name'] = lines[0]
            
        bill_to_match = re.search(r'(?i)(?:bill\s*to|customer|buyer)\s*[:\-]?\s*\n?([A-Za-z\s]+)', text)
        if bill_to_match:
            buyer_name = bill_to_match.group(1).strip()
            # Clean up trailing noise
            buyer_name = buyer_name.split('\n')[0].replace('GSTIN', '').strip()
            if buyer_name:
                data['buyer_name'] = buyer_name
                
        # Total Tax
        if data.get('cgst') is not None and data.get('sgst') is not None:
            data['total_tax'] = data.get('cgst') + data.get('sgst')
        elif data.get('igst') is not None:
            data['total_tax'] = data.get('igst')
            
        return data

extraction_service = ExtractionService()
