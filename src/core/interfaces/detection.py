"""
Detection interfaces for game state detection and management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.games import Game


@dataclass
class DetectionResult:
    """Result of a detection operation."""

    game: Optional[Game]
    state: Optional[str]
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class StateTransition:
    """Represents a state transition with context."""

    from_state: Optional[str]
    to_state: str
    game: Game
    timestamp: float
    triggered_patterns: List[str]


class IDetectionEngine(ABC):
    """Main detection engine interface."""

    @abstractmethod
    def detect_and_control(self) -> DetectionResult:
        """Perform detection and control recording."""

    @abstractmethod
    def can_save_lastplay(self) -> bool:
        """Check if lastplay can be saved."""

    @abstractmethod
    def save_current_lastplay(self) -> Tuple[bool, str]:
        """Save the current lastplay."""

    @abstractmethod
    def get_current_status(self) -> Dict[str, Any]:
        """Get current engine status."""


class IGameDetector(ABC):
    """Interface for detecting which game is currently active."""

    @abstractmethod
    def get_active_game(self) -> Optional[Game]:
        """Get the currently active game."""

    @abstractmethod
    def is_game_focused(self, game: Game) -> bool:
        """Check if a specific game is focused."""


class IStateDetector(ABC):
    """Interface for detecting game states."""

    @abstractmethod
    def detect_state(self, game: Game) -> Optional[str]:
        """Detect the current state for a given game."""

    @abstractmethod
    def can_handle_game(self, game: Game) -> bool:
        """Check if this detector can handle the given game type."""
