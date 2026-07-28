from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuctionRunRequest(BaseModel):
    auction_type: Literal["first_price", "second_price"] = "first_price"
    num_rounds: int = Field(1000, gt=0, le=20_000)
    bidder_count: int = Field(6, ge=1, le=16)
    strategy: Literal["truthful", "shading", "bandit", "mixed"] = "mixed"
    alpha: float = Field(0.8, ge=0)
    low_value: float = 0.0
    high_value: float = 100.0
    seed: int = 42

    @model_validator(mode="after")
    def validate_range(self):
        if self.low_value > self.high_value:
            raise ValueError("low_value must not exceed high_value")
        return self


class MarketRunRequest(BaseModel):
    num_rounds: int = Field(1000, gt=0, le=20_000)
    num_buyers: int = Field(8, ge=1, le=16)
    num_sellers: int = Field(8, ge=1, le=16)
    buyer_strategy: Literal["truthful", "shading", "bandit"] = "truthful"
    seller_strategy: Literal["truthful", "markup"] = "truthful"
    buyer_alpha: float = Field(0.8, ge=0)
    seller_markup: float = Field(0.2, ge=0)
    buyer_value_low: float = 0.0
    buyer_value_high: float = 100.0
    seller_cost_low: float = 0.0
    seller_cost_high: float = 100.0
    seed: int = 42

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.buyer_value_low > self.buyer_value_high:
            raise ValueError("buyer_value_low must not exceed buyer_value_high")
        if self.seller_cost_low > self.seller_cost_high:
            raise ValueError("seller_cost_low must not exceed seller_cost_high")
        return self


class LearningRunRequest(BaseModel):
    num_rounds: int = Field(1000, gt=0, le=20_000)
    epsilon: float = Field(0.1, ge=0, le=1)
    seed: int = 42


class SimulationResponse(BaseModel):
    run_id: uuid.UUID | None = None
    results: list[dict[str, Any]]
    agent_summary: list[dict[str, Any]]
    summary: dict[str, Any]
    cumulative_profit: list[dict[str, Any]] | None = None
    action_summary: list[dict[str, Any]] | None = None
    action_history: list[dict[str, Any]] | None = None


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    description: str
    kind: str
    parameters: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ExperimentRunRequest(BaseModel):
    overrides: dict[str, Any] = Field(default_factory=dict)


class ExperimentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    experiment_id: uuid.UUID | None
    kind: str
    status: str
    parameters: dict[str, Any]
    summary: dict[str, Any]
    result: dict[str, Any]
    error: str | None
    created_at: datetime
