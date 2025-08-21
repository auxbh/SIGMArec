"""
Game classes for different detection types.
"""

from typing import Dict, List, Optional

from mss.screenshot import ScreenShot

from .base import Game
from .log import LogState
from .pixel import PixelState
from .process import ProcessInfo
from .types import GameType


class LogGame(Game):
    """A game that uses log-based detection."""

    def __init__(
        self,
        name: str,
        shortname: str,
        processes: List[ProcessInfo],
        logs: str,
        states: Dict[str, LogState],
    ):
        super().__init__(name, shortname, processes)
        self.logs = logs
        self.states = states

    @property
    def game_type(self) -> GameType:
        """Get the type of this game."""
        return GameType.LOG

    def get_current_state(self, context: List[Dict]) -> Optional[LogState]:
        """
        Detect the current game state from log entries.
        The last pattern found in the log entries dictates the current state.

        Args:
            log_entries: List of dictionaries with 'class' and 'method' keys
        """
        if not context:
            return None

        latest_state = None
        latest_position = -1

        for state in self.states.values():
            last_match_pos = state.get_last_match_position(context)
            if last_match_pos > latest_position:
                latest_position = last_match_pos
                latest_state = state

        return latest_state

    def get_playing_state_timestamp(self, context: List[Dict]) -> Optional[str]:
        """
        Get the timestamp of the last Playing state detection.

        Args:
            log_entries: List of dictionaries with 'class', 'method', and 'date' keys

        Returns:
            Timestamp string of the last Playing state match, or None if no Playing state found
        """
        if not context:
            return None

        playing_state = self.states.get("Playing")
        if not playing_state:
            return None

        timestamp = playing_state.get_last_match_timestamp(context)
        return timestamp if timestamp else None

    def get_state_names(self) -> List[str]:
        """Get all available state names for this game."""
        return list(self.states.keys())

    @classmethod
    def from_config(cls, name: str, config: Dict) -> "LogGame":
        """Create a LogGame from configuration data."""
        processes = [
            ProcessInfo(exe=proc.get("exe", ""), title=proc.get("title", ""))
            for proc in config.get("processes", [])
        ]
        states = {}

        for state_name, state_config in config.get("states", {}).items():
            states[state_name] = LogState.from_config(state_name, state_config)

        return cls(
            name=name,
            shortname=config.get("shortname", name),
            processes=processes,
            logs=config.get("logs", ""),
            states=states,
        )


class PixelGame(Game):
    """A game that uses pixel-based detection."""

    def __init__(
        self,
        name: str,
        shortname: str,
        processes: List[ProcessInfo],
        states: Dict[str, PixelState],
    ):
        super().__init__(name, shortname, processes)
        self.states = states

    @property
    def game_type(self) -> GameType:
        """Get the type of this game."""
        return GameType.PIXEL

    def get_current_state(self, context: ScreenShot) -> Optional[PixelState]:
        """Detect the current game state from a screenshot."""
        for state in self.states.values():
            if state.matches(context):
                return state
        return None

    def get_state_names(self) -> List[str]:
        """Get all available state names for this game."""
        return list(self.states.keys())

    @classmethod
    def from_config(cls, name: str, config: Dict) -> "PixelGame":
        """Create a PixelGame from configuration data."""
        processes = [
            ProcessInfo(exe=proc.get("exe", ""), title=proc.get("title", ""))
            for proc in config.get("processes", [])
        ]
        states = {}

        for state_name, state_config in config.get("states", {}).items():
            states[state_name] = PixelState.from_config(state_name, state_config)

        return cls(
            name=name,
            shortname=config.get("shortname", name),
            processes=processes,
            states=states,
        )
