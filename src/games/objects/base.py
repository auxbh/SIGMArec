"""
Abstract base classes and interfaces for SIGMArec.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union

from .process import ProcessInfo
from .types import GameType


class Pattern(ABC):
    """Abstract base class for detection patterns."""

    @abstractmethod
    def matches(self, context) -> bool:
        """Check if this pattern matches the given context."""

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of this pattern."""

    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict, **kwargs):
        """Create a pattern from src.configuration data."""


class State(ABC):
    """Abstract base class for game states."""

    @abstractmethod
    def matches(self, context) -> bool:
        """Check if this state matches the given context."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this state."""

    @abstractmethod
    def get_pattern_descriptions(self) -> List[str]:
        """Get descriptions of all patterns in this state."""


class Game(ABC):
    """Abstract base class for all game definitions."""

    def __init__(self, name: str, shortname: str, processes: List[ProcessInfo]):
        self.name = name
        self.shortname = shortname
        self.processes = processes

    @property
    @abstractmethod
    def game_type(self) -> GameType:
        """Get the type of this game."""

    @abstractmethod
    def get_current_state(self, context) -> Union["State", None]:
        """Detect the current game state from the given context."""

    @abstractmethod
    def get_state_names(self) -> List[str]:
        """Get all available state names for this game."""

    @classmethod
    @abstractmethod
    def from_config(cls, name: str, config: Dict) -> "Game":
        """Create a Game from src.configuration data."""

    def is_process_running(self, process_name: str, window_title: str = "") -> bool:
        """Check if any of the game's processes are running."""
        return any(
            proc.matches_process(process_name, window_title) for proc in self.processes
        )

    def get_info(self) -> Dict[str, Union[str, int]]:
        """Get basic information about this game."""
        return {
            "name": self.name,
            "shortname": self.shortname,
            "type": self.game_type.value,
            "processes": len(self.processes),
            "states": len(self.get_state_names()),
        }
