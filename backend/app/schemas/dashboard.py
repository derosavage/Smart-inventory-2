from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class LowStockAlert(BaseModel):
    sku: str
    name: str
    quantity_in_stock: int
    reorder_threshold: int
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None


class DailySalesSummary(BaseModel):
    transaction_date: date
    total_transactions: int
    total_items_sold: int
    total_revenue: Decimal


class CurrentInventoryItem(BaseModel):
    sku: str
    barcode: Optional[str] = None
    name: str
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None
    quantity_in_stock: int
    reorder_threshold: int
    cost_price: Decimal
    selling_price: Decimal
    is_active: bool


class ProductPerformance(BaseModel):
    sku: str
    name: str
    category_name: Optional[str] = None
    quantity_in_stock: int
    total_sold_30d: int
    avg_daily_sales: float
    turnover_rate: Optional[float] = None


class DashboardSummary(BaseModel):
    total_products: int
    total_stock_value: Decimal | float
    low_stock_count: int
    out_of_stock_count: int
    today_sales: Optional[DailySalesSummary] = None
