"""
Game detection - determines which game is currently focused.
"""

from typing import List, Optional

import psutil
import win32gui
import win32process

from core.interfaces import IGameDetector
from detection.log_service import LogService
from detection.screen_capture import ScreenCaptureService
from games import Game, LogGame, PixelGame, ProcessInfo


class GameDetector(IGameDetector):
    """Detects which game is currently active/focused."""

    def __init__(self, games: List[Game]):
        """
        Initialize game detector.

        Args:
            games: List of games to detect
        """
        self.games = games
        self.screen = ScreenCaptureService()
        self.logs = LogService()

    def get_active_game(self) -> Optional[Game]:
        """
        Get the currently active/focused game.

        Returns:
            Active game or None if no game is focused
        """
        window_title = self.screen.get_focused_window_title()
        if not window_title:
            return None

        if self._foreground_is_java():
            for game in self.games:
                if isinstance(game, LogGame) and self._matches_focused(
                    game, window_title
                ):
                    return game

        for game in self.games:
            if isinstance(game, PixelGame) and self._matches_focused(
                game, window_title
            ):
                return game

        return None

    def is_game_focused(self, game: Game) -> bool:
        """
        Check if a specific game is currently focused.

        Args:
            game: Game to check

        Returns:
            True if the game is focused
        """
        window_title = self.screen.get_focused_window_title()
        if not window_title:
            return False

        return self._matches_focused(game, window_title)

    def _foreground_is_java(self) -> bool:
        """Check if foreground process is Java."""
        return self.logs.get_foreground_java_process_info() is not None

    def _matches_focused(self, game: Game, window_title: str) -> bool:
        """
        Check if game matches the focused window.

        Args:
            game: Game to check
            window_title: Current window title

        Returns:
            True if game matches focused window
        """
        process_name = self._focused_process_name()
        if not process_name:
            return False

        for process_info in game.processes:
            if isinstance(process_info, ProcessInfo):
                if process_info.matches_process(process_name, window_title):
                    return True

        return False

    def _focused_process_name(self) -> Optional[str]:
        """Get the name of the focused process."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
