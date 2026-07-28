"""Compatibility entry point; prefer ``backend.app.main:app``."""

from backend.app.main import app

__all__ = ["app"]
