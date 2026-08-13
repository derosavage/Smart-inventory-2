from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class UserAdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = "clerk"
    is_active: bool = True


class UserAdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: Optional[str] = None


class SettingCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: str
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class SettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    description: Optional[str] = None
    updated_by: Optional[int] = None
    updated_by_username: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AuditLogEntry(BaseModel):
    id: int
    table_name: str
    record_id: Optional[int] = None
    operation: str
    old_data: Optional[Any] = None
    new_data: Optional[Any] = None
    changed_by: Optional[int] = None
    changed_by_username: Optional[str] = None
    changed_at: datetime


class AuditLogFilter(BaseModel):
    table_name: Optional[str] = None
    user_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    operation: Optional[str] = None


# ---------- Branch Schema ----------
class BranchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class BranchResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------- Commission Schema ----------
class CommissionRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    commission_type: str = Field("percentage", pattern="^(percentage|fixed)$")
    rate: float = Field(..., ge=0, le=100)
    target_type: str = Field(..., pattern="^(staff|product|category)$")
    target_id: Optional[int] = None


class CommissionRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    rate: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class CommissionRuleResponse(BaseModel):
    id: int
    name: str
    commission_type: str
    rate: float
    target_type: str
    target_id: Optional[int] = None
    is_active: bool
    created_at: datetime


# ---------- Profit & Loss Schema ----------
class ProfitLossReport(BaseModel):
    from_date: str
    to_date: str
    total_revenue: float
    total_cogs: float
    gross_profit: float
    total_expenses: float
    net_profit: float
    total_items_sold: int
    total_tax_collected: float


# ---------- Daily Business Report Schema ----------
class DailyBusinessReport(BaseModel):
    date: str
    sales: dict
    top_product: Optional[dict] = None
    movements: dict
    low_stock_count: int
    out_of_stock_count: int
