"""
Log-based state detection for Java games that write to log files.
"""

import logging
from typing import Optional

from detection.detectors.base import BaseStateDetector
from detection.log_service import LogService
from games import Game, LogGame


class LogStateDetector(BaseStateDetector):
    """Detector for log-based game state detection."""

    def __init__(self, detection_threshold: int = 2):
        super().__init__(detection_threshold)
        self.logs = LogService()

    def can_handle_game(self, game: Game) -> bool:
        """Check if this detector can handle log-based games."""
        return isinstance(game, LogGame)

    def _detect_raw_state(self, game: Game) -> Optional[str]:
        """
        Detect state using log analysis.

        Args:
            game: LogGame to analyze

        Returns:
            Detected state name or None
        """
        if not isinstance(game, LogGame):
            logging.warning("[LogDetector] Cannot handle non-log game: %s", game.name)
            return None

        entries = self.logs.get_log_entries_for_game(game.name, game.logs)
        if not entries:
            return None

        state_obj = game.get_current_state(entries)
        return state_obj.get_name() if state_obj else None
