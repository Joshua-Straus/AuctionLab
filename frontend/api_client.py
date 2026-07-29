from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests


class ApiError(RuntimeError):
    pass


class SimulatorApiClient:
    def __init__(self, base_url: str | None = None, timeout: int = 120):
        self.base_url = (
            base_url or os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        ).rstrip("/")
        self.timeout = timeout

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> Any:
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            detail = ""
            if getattr(error, "response", None) is not None:
                try:
                    detail = f": {error.response.json().get('detail')}"
                except (ValueError, AttributeError):
                    detail = f": {error.response.text}"
            raise ApiError(f"Backend request failed{detail}") from error
        return response.json()

    @staticmethod
    def _as_dashboard_result(payload: dict[str, Any], kind: str) -> dict[str, Any]:
        result = {
            **payload,
            "results": pd.DataFrame(payload["results"]),
            "agent_summary": pd.DataFrame(payload["agent_summary"]),
        }
        result["auction_summary"] = payload["summary"]
        for key in (
            "cumulative_profit",
            "action_summary",
            "action_history",
            "strategy_summary",
        ):
            if payload.get(key) is not None:
                result[key] = pd.DataFrame(payload[key])
        return result

    def run_auction(self, parameters: dict[str, Any]) -> dict[str, Any]:
        payload = self._request("POST", "/simulations/auctions", parameters)
        return self._as_dashboard_result(payload, "auction")

    def run_learning(self, parameters: dict[str, Any]) -> dict[str, Any]:
        payload = self._request("POST", "/simulations/learning", parameters)
        return self._as_dashboard_result(payload, "learning")

    def run_vickrey(self, parameters: dict[str, Any]) -> dict[str, Any]:
        payload = self._request("POST", "/simulations/vickrey", parameters)
        return self._as_dashboard_result(payload, "vickrey")

    def run_first_price_strategies(
        self, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        payload = self._request(
            "POST", "/simulations/first-price-strategies", parameters
        )
        return self._as_dashboard_result(payload, "first_price")

    def list_experiments(self) -> list[dict[str, Any]]:
        return self._request("GET", "/experiments")

    def run_experiment(
        self, slug: str, kind: str, overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        payload = self._request(
            "POST", f"/experiments/{slug}/run", {"overrides": overrides or {}}
        )
        return self._as_dashboard_result(payload, kind)
