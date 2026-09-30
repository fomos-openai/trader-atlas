from __future__ import annotations


class TraderAtlasError(Exception):
    """Base exception for expected command failures."""


class ConfigurationError(TraderAtlasError):
    """Raised when a configuration is incomplete or unsafe."""


class DataContractError(TraderAtlasError):
    """Raised when local market data violates the canonical contract."""
