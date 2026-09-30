"""Invoice Intelligence Service.

Coordinates the complete Phase 2 intelligence pipeline to produce a
unified, explainable result for a document.
"""

from fastapi import HTTPException, status

from app.schemas.classification import DocumentType
from app.schemas.invoice_intelligence import (
    IntelligenceIssue,
    IntelligenceIssueStatus,
    IntelligenceOverallStatus,
    InvoiceIntelligenceResult,
)
from app.schemas.tax_type_validation import TaxTypeValidationStatus
from app.schemas.math_validation import OverallMathStatus, MathCheckStatus

from app.services.document_service import document_service
from app.services.classification_service import classification_service
from app.services.extraction_service import extraction_service
from app.services.gstin_validation_service import gstin_validation_service
from app.services.state_detection_service import state_detection_service
from app.services.gst_tax_type_validation_service import gst_tax_type_validation_service
from app.services.math_validation_service import math_validation_service



class InvoiceIntelligenceService:
    def generate_intelligence(self, document_id: str) -> InvoiceIntelligenceResult:
        """Run the full invoice intelligence pipeline and return a unified result."""
        
        # 1. Verify document exists
        # Raises 404 if not found
        document_service.get_document_path_and_mime_type(document_id)

        # 2. Get classification
        classification = classification_service.classify_document(document_id)
        
        # If not an invoice, return early with INFORMATION_FOUND
        if classification.document_type != DocumentType.INVOICE:
            return InvoiceIntelligenceResult(
                document_id=document_id,
                document_type=classification.document_type,
                overall_status=IntelligenceOverallStatus.INFORMATION_FOUND,
                summary=f"Document classified as {classification.document_type.value}. Invoice-specific intelligence was not applied.",
                classification=classification,
            )
            
        # 3. Get extraction (Canonical Invoice)
        try:
            invoice = extraction_service.get_extraction_result(document_id)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invoice extraction result unavailable. Please ensure extraction has been completed."
                )
            raise e

        # 4. GSTIN Validation
        seller_gstin = invoice.seller.gstin if invoice.seller else None
        buyer_gstin = invoice.buyer.gstin if invoice.buyer else None
        
        seller_gstin_val = gstin_validation_service.validate(seller_gstin)
        buyer_gstin_val = gstin_validation_service.validate(buyer_gstin)
        
        # 5. State Detection
        seller_state = state_detection_service.detect_state(seller_gstin)
        buyer_state = state_detection_service.detect_state(buyer_gstin)
        jurisdiction_relationship = state_detection_service.compare_jurisdictions(seller_state, buyer_state)
        
        from app.schemas.validation import DocumentGSTINValidationResponse
        from app.schemas.state_detection import DocumentStateDetectionResponse
        
        gstin_resp = DocumentGSTINValidationResponse(
            document_id=document_id,
            seller_gstin=seller_gstin_val,
            buyer_gstin=buyer_gstin_val
        )
        state_resp = DocumentStateDetectionResponse(
            document_id=document_id,
            seller=seller_state,
            buyer=buyer_state,
            jurisdiction_relationship=jurisdiction_relationship
        )
        
        # 6. Tax Type Validation
        tax_type_val = gst_tax_type_validation_service.validate(
            document_id=document_id,
            jurisdiction=jurisdiction_relationship,
            financials=invoice.financials
        )
        
        # 7. Mathematical Validation
        math_val = math_validation_service.validate(invoice)
        
        # 8. Compile Issues & Overall Status
        issues = []
        has_mismatch = False
        has_review = False
        
        # --- GSTIN Issues ---
        if not seller_gstin_val.is_valid:
            if "MISSING_GSTIN" in seller_gstin_val.errors:
                has_review = True
                issues.append(IntelligenceIssue(
                    category="GSTIN",
                    status=IntelligenceIssueStatus.REVIEW_REQUIRED,
                    field="seller.gstin",
                    explanation="Seller GSTIN was not found in the extracted data.",
                    recommendation="Provide the missing seller GSTIN if available."
                ))
            else:
                has_mismatch = True
                issues.append(IntelligenceIssue(
                    category="GSTIN",
                    status=IntelligenceIssueStatus.MISMATCH,
                    field="seller.gstin",
                    explanation=f"Seller GSTIN '{seller_gstin}' failed format/checksum validation.",
                    recommendation="Review the extracted seller GSTIN for OCR errors or invalid data."
                ))
            
        if not buyer_gstin_val.is_valid:
            if "MISSING_GSTIN" in buyer_gstin_val.errors:
                has_review = True
                issues.append(IntelligenceIssue(
                    category="GSTIN",
                    status=IntelligenceIssueStatus.REVIEW_REQUIRED,
                    field="buyer.gstin",
                    explanation="Buyer GSTIN was not found in the extracted data.",
                    recommendation="Provide the missing buyer GSTIN if available."
                ))
            else:
                has_mismatch = True
                issues.append(IntelligenceIssue(
                    category="GSTIN",
                    status=IntelligenceIssueStatus.MISMATCH,
                    field="buyer.gstin",
                    explanation=f"Buyer GSTIN '{buyer_gstin}' failed format/checksum validation.",
                    recommendation="Review the extracted buyer GSTIN for OCR errors or invalid data."
                ))
            
        # --- Tax Type Issues ---
        if tax_type_val.status == TaxTypeValidationStatus.MISMATCH:
            has_mismatch = True
            for err in tax_type_val.errors:
                issues.append(IntelligenceIssue(
                    category="Tax Type",
                    status=IntelligenceIssueStatus.MISMATCH,
                    explanation=err,
                    recommendation="Review the tax type components against the jurisdiction relationship."
                ))
        elif tax_type_val.status == TaxTypeValidationStatus.REVIEW_REQUIRED:
            has_review = True
            for warn in tax_type_val.warnings:
                issues.append(IntelligenceIssue(
                    category="Tax Type",
                    status=IntelligenceIssueStatus.REVIEW_REQUIRED,
                    explanation=warn,
                    recommendation="Review missing or zero-valued tax components."
                ))
                
        # --- Mathematical Issues ---
        if math_val.status == OverallMathStatus.MISMATCH:
            has_mismatch = True
            for chk_name, chk_res in math_val.checks.items():
                if chk_res.status == MathCheckStatus.MISMATCH:
                    issues.append(IntelligenceIssue(
                        category=f"Mathematical - {chk_res.check_name}",
                        status=IntelligenceIssueStatus.MISMATCH,
                        explanation=chk_res.message,
                        recommendation="Verify the financial values extracted from the document."
                    ))
        elif math_val.status == OverallMathStatus.REVIEW_REQUIRED:
            has_review = True
            for chk_name, chk_res in math_val.checks.items():
                if chk_res.status == MathCheckStatus.REVIEW_REQUIRED:
                    issues.append(IntelligenceIssue(
                        category=f"Mathematical - {chk_res.check_name}",
                        status=IntelligenceIssueStatus.REVIEW_REQUIRED,
                        explanation=chk_res.message,
                        recommendation="Provide missing financial values to complete mathematical validation."
                    ))
                    
        # 9. Aggregate Overall Status
        if has_mismatch:
            overall = IntelligenceOverallStatus.MISMATCH
            summary = "Invoice contains critical mismatches in structural, tax-type, or mathematical validation."
        elif has_review:
            overall = IntelligenceOverallStatus.REVIEW_REQUIRED
            summary = "Invoice requires manual review due to missing data or indeterminate validation results."
        else:
            overall = IntelligenceOverallStatus.CONSISTENT
            summary = "Invoice successfully passed all deterministic GSTIN, tax-type, and mathematical validations."
            
        return InvoiceIntelligenceResult(
            document_id=document_id,
            document_type=DocumentType.INVOICE,
            overall_status=overall,
            summary=summary,
            classification=classification,
            extraction=invoice,
            gstin_validation=gstin_resp,
            state_detection=state_resp,
            tax_type_validation=tax_type_val,
            mathematical_validation=math_val,
            issues=issues
        )

invoice_intelligence_service = InvoiceIntelligenceService()
