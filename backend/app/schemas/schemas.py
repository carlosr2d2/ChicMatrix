from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class RetailerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    base_url: str
    is_active: bool


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    image_url: str | None
    category: str | None
    brand: str | None
    color: str | None
    retailer_id: int


class PriceComparison(BaseModel):
    retailer_id: int
    retailer_name: str
    amount: float
    currency: str
    scraped_at: datetime


class RecommendationItem(BaseModel):
    product: ProductResponse
    score: float
    reasons: list[str] = Field(default_factory=list)
    prices: list[PriceComparison] = Field(default_factory=list)
    best_price: PriceComparison | None = None


class RecommendationResponse(BaseModel):
    user_id: UUID
    recommendations: list[RecommendationItem]


class ScrapeResponse(BaseModel):
    retailer_id: int
    task_id: str
    status: str
    message: str
