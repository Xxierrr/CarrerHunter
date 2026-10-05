"""
Source Adapter Registry — maps adapter names to adapter classes.
Adding a new source = creating one adapter class + registering it here.
"""

from typing import Type
from app.crawlers.base import JobSourceAdapter

# Registry of all adapters
_ADAPTER_REGISTRY: dict[str, Type[JobSourceAdapter]] = {}


def register_adapter(name: str):
    """Decorator to register a source adapter."""
    def wrapper(cls: Type[JobSourceAdapter]):
        _ADAPTER_REGISTRY[name] = cls
        cls.name = name
        return cls
    return wrapper


def get_adapter(name: str, config: dict | None = None) -> JobSourceAdapter:
    """Get an adapter instance by name."""
    if name not in _ADAPTER_REGISTRY:
        raise ValueError(f"Unknown adapter: {name}. Available: {list(_ADAPTER_REGISTRY.keys())}")
    return _ADAPTER_REGISTRY[name](config=config)


def list_adapters() -> dict[str, Type[JobSourceAdapter]]:
    """List all registered adapters."""
    return _ADAPTER_REGISTRY.copy()


# Import all adapter modules to trigger registration
def load_all_adapters():
    """Import all adapter modules to populate the registry."""
    from app.crawlers.adapters import (  # noqa: F401
        greenhouse,
        lever,
        ashby,
        smartrecruiters,
        generic_career_page,
    )
