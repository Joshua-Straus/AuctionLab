"""
File to define configuration settings for auction simulation experiments.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """
    Stores settings for one simulation experiment.
    """

    auction_type: str = "first_price"
    num_rounds: int = 10_000
    low_value: float = 0.0
    high_value: float = 100.0
    seed: int | None = 42
    output_dir: str = "outputs"
