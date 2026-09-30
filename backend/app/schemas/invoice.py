from typing import List, Optional
from pydantic import BaseModel, Field

class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    taxable_amount: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    total: Optional[float] = None

class InvoiceExtractionResult(BaseModel):
    document_id: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    seller_name: Optional[str] = None
    seller_gstin: Optional[str] = None
    seller_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_address: Optional[str] = None
    taxable_amount: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    igst: Optional[float] = None
    total_tax: Optional[float] = None
    grand_total: Optional[float] = None
    line_items: Optional[List[LineItem]] = Field(default_factory=list)
