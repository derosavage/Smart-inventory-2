from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel

# ---------- Sales Report ----------
class SalesReportFilter(BaseModel):
    from_date: date
    to_date: date
    group_by: str = "day"  # day, week, month

class SalesReportItem(BaseModel):
    period: str
    transaction_count: int
    items_sold: int
    revenue: Decimal
    tax_collected: Optional[Decimal] = None

# ---------- Stock Movement Report ----------
class StockMovementFilter(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    product_sku: Optional[str] = None
    movement_type: Optional[str] = None

class StockMovementReportItem(BaseModel):
    id: int
    datetime: datetime
    product_sku: str
    product_name: str
    movement_type: str
    quantity: int
    previous_quantity: int
    new_quantity: int
    reason: Optional[str]
    performed_by: str

# ---------- Product Performance Report ----------
class ProductPerformanceFilter(BaseModel):
    sort_by: str = "total_sold_30d"  # total_sold_30d, avg_daily_sales, stock
    limit: int = 50

class ProductPerformanceItem(BaseModel):
    sku: str
    name: str
    category: Optional[str]
    current_stock: int
    total_sold_30d: int
    avg_daily_sales: float
    turnover_rate: Optional[float]  # (total_sold_30d / current_stock) if stock>0
    status: str

# ---------- Profit & Loss Report ----------
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

# ---------- Daily Business Report ----------
class DailyBusinessReport(BaseModel):
    date: str
    sales: dict
    top_product: Optional[dict] = None
    movements: dict
    low_stock_count: int
    out_of_stock_count: int