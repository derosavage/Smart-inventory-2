from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    expires_in_days: Optional[int] = Field(None, ge=1)


class ApiKeyRegenerate(BaseModel):
    confirm: bool = True


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    api_key: str
    expires_at: Optional[datetime] = None
    created_by: int
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime


class WebhookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    url: HttpUrl
    events: List[str] = Field(..., min_length=1)
    secret: Optional[str] = None


class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: int
    name: str
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None
    created_by: int
    is_active: bool
    created_at: datetime


class WebhookDeliveryResponse(BaseModel):
    id: int
    webhook_id: int
    webhook_name: Optional[str] = None
    event: str
    payload: Any
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    success: bool
    attempted_at: datetime


class IntegrationStatus(BaseModel):
    total_api_keys: int
    active_api_keys: int
    total_webhooks: int
    active_webhooks: int
    recent_deliveries: List[WebhookDeliveryResponse]
