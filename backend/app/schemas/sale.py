from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    sku: str
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)


class SaleCreate(BaseModel):
    transaction_number: str
    transaction_date: datetime
    items: List[SaleItemCreate]
    tax_type: Optional[str] = "standard"
    tax_amount: Optional[Decimal] = Decimal("0.00")
    branch_id: Optional[int] = None
    notes: Optional[str] = None


class SaleItemResponse(BaseModel):
    id: int
    transaction_id: int
    product_sku: str
    quantity: int
    unit_price: Decimal
    line_total: Optional[Decimal] = None
    product_name: Optional[str] = None


class SaleTransactionResponse(BaseModel):
    id: int
    transaction_number: str
    user_id: int
    username: Optional[str] = None
    total_amount: Decimal
    transaction_date: datetime
    tax_type: Optional[str] = "standard"
    tax_amount: Optional[Decimal] = Decimal("0.00")
    branch_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[SaleItemResponse] = []


class SaleSummaryResponse(BaseModel):
    total_transactions: int
    total_revenue: Decimal
    total_items_sold: int
