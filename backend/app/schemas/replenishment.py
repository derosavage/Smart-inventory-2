from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ReplenishmentSuggestionCreate(BaseModel):
    lookback_days: int = Field(30, ge=1)
    forecast_days: int = Field(7, ge=1)
    safety_stock_factor: float = Field(1.5, gt=0)


class ReplenishmentSuggestionResponse(BaseModel):
    id: int
    product_sku: str
    product_name: str
    product_barcode: Optional[str] = None
    suggested_quantity: int
    current_stock: int
    predicted_demand: Optional[float] = None
    safety_stock: Optional[float] = None
    is_acted_upon: bool
    date_generated: datetime
    acted_upon_at: Optional[datetime] = None


class ReplenishmentAction(BaseModel):
    suggestion_id: int
    action: Literal["accept", "ignore"]
