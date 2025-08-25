"""
Handles OBS scene switching based on game states.
"""

from config.settings import AppSettings
from core.interfaces.obs import IOBSController


class VideoProcessor:
    """Processes state transitions to control OBS video settings."""

    def __init__(self, obs_controller: IOBSController, settings: AppSettings):
        """
        Initialize video processor.

        Args:
            obs_controller: OBS controller for video operations
            settings: Application settings containing video settings
        """
        self.obs = obs_controller
        self.settings = settings

    def process_game_change(self, game) -> None:
        """
        Handle game focus change by switching OBS video settings based on game.

        Args:
            game: New focused game or None if no game focused
        """
        if game is None:
            return None

        game_video_settings = self.obs.get_game_video_settings(game.shortname)
        if game_video_settings is None:
            return None

        current_video_settings = self.obs.get_video_settings()
        if current_video_settings is None:
            return None

        if game_video_settings != current_video_settings:
            self.obs.set_video_settings(game_video_settings)
