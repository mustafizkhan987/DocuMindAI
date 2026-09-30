from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal

class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    taxable_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total: Optional[Decimal] = None

class Party(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
    address: Optional[str] = None

class Financials(BaseModel):
    taxable_amount: Optional[Decimal] = None
    cgst: Optional[Decimal] = None
    sgst: Optional[Decimal] = None
    igst: Optional[Decimal] = None
    total_tax: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None

class CanonicalInvoice(BaseModel):
    document_id: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    seller: Party = Field(default_factory=Party)
    buyer: Party = Field(default_factory=Party)
    financials: Financials = Field(default_factory=Financials)
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    due_date: Optional[str] = None
    contact: Optional[str] = None
    place_of_supply: Optional[str] = None
    line_items: List[LineItem] = Field(default_factory=list)

# Alias for backward compatibility in internal references
InvoiceExtractionResult = CanonicalInvoice
