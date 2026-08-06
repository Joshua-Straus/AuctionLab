from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuctionRunRequest(BaseModel):
    auction_type: Literal[
        "first_price", "second_price", "english", "dutch"
    ] = "first_price"
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
        if (
            self.auction_type in {"english", "dutch"}
            and self.low_value == self.high_value
        ):
            raise ValueError("Clock auctions require a non-empty bid range")
        return self


class LearningRunRequest(BaseModel):
    num_rounds: int = Field(1000, gt=0, le=20_000)
    epsilon: float = Field(0.1, ge=0, le=1)
    seed: int = 42


class VickreyRunRequest(BaseModel):
    num_rounds: int = Field(5000, gt=0, le=20_000)
    bidder_count: int = Field(6, ge=2, le=64)
    bid_spread: float = Field(20.0, gt=0)
    bid_count: int = Field(9, ge=3, le=21)
    low_value: float = 0.0
    high_value: float = 100.0
    seed: int = 42

    @model_validator(mode="after")
    def validate_range(self):
        if self.low_value > self.high_value:
            raise ValueError("low_value must not exceed high_value")
        if self.bid_count % 2 == 0:
            raise ValueError("bid_count must be odd so the grid includes truth-telling")
        return self


class FirstPriceStrategyRunRequest(BaseModel):
    num_rounds: int = Field(5000, gt=0, le=20_000)
    agents_per_strategy: int = Field(3, ge=1, le=3)
    shading_alpha: float = Field(0.8, ge=0, le=1.2)
    epsilon: float = Field(0.1, ge=0, le=1)
    low_value: float = 0.0
    high_value: float = 100.0
    seed: int = 42

    @model_validator(mode="after")
    def validate_range(self):
        if self.low_value > self.high_value:
            raise ValueError("low_value must not exceed high_value")
        return self


class RevenueEqualityRunRequest(BaseModel):
    num_rounds: int = Field(10_000, ge=100, le=20_000)
    bidder_count: int = Field(16, ge=2, le=64)
    low_value: float = 0.0
    high_value: float = 100.0
    seed: int = 42

    @model_validator(mode="after")
    def validate_range(self):
        if self.low_value > self.high_value:
            raise ValueError("low_value must not exceed high_value")
        return self


class SimulationResponse(BaseModel):
    run_id: uuid.UUID | None = None
    results: list[dict[str, Any]]
    agent_summary: list[dict[str, Any]]
    summary: dict[str, Any]
    cumulative_profit: list[dict[str, Any]] | None = None
    action_summary: list[dict[str, Any]] | None = None
    action_history: list[dict[str, Any]] | None = None
    strategy_summary: list[dict[str, Any]] | None = None
    proposition: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    revenue_by_trial: list[dict[str, Any]] | None = None
    format_summary: list[dict[str, Any]] | None = None


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
