from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    created_at: datetime


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    barcode: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    cost_price: Decimal = Field(..., ge=0)
    selling_price: Decimal = Field(..., ge=0)
    quantity_in_stock: int = Field(0, ge=0)
    reorder_threshold: int = Field(5, ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    barcode: Optional[str] = Field(None, min_length=1, max_length=128)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    reorder_threshold: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    sku: str
    barcode: str
    name: str
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    cost_price: Decimal
    selling_price: Decimal
    quantity_in_stock: int
    reorder_threshold: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None
