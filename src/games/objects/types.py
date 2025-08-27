"""
Type definitions and enums for SIGMArec.
"""

from enum import Enum
from typing import Any, Dict, Protocol


class GameType(Enum):
    """Enumeration of supported game detection types."""

    LOG = "log"
    PIXEL = "pixel"


class Detectable(Protocol):
    """Protocol for objects that can be detected/matched."""

    def matches(self, context: Any) -> bool:
        """Check if this object matches the given context."""


class Parseable(Protocol):
    """Protocol for objects that can be parsed from src.configuration."""

    @classmethod
    def from_config(cls, config: Dict[str, Any], **kwargs):
        """Create an instance from src.configuration data."""
