"""
Handles OBS scene switching based on game states.
"""

import logging
import time

from core.interfaces.obs import IOBSController
from core.interfaces.detection import StateTransition
from config.settings import AppSettings


class SceneProcessor:
    """Processes state transitions to control OBS scene switching."""

    def __init__(self, obs_controller: IOBSController, settings: AppSettings):
        """
        Initialize scene processor.

        Args:
            obs_controller: OBS controller for scene operations
            settings: Application settings containing scene mappings
        """
        self.obs = obs_controller
        self.settings = settings
        self._last_scene_change_time: float = 0.0

    def process_transition(self, transition: StateTransition) -> None:
        """
        Process a state transition and switch scenes accordingly.

        Args:
            transition: State transition to process
        """
        if not transition.game:
            return

        game_shortname = transition.game.shortname
        scene_name = self.settings.get_scene_name(game_shortname, transition.to_state)

        if scene_name:
            current_scene = self.obs.get_current_scene()
            if current_scene != scene_name:
                self.obs.set_current_scene(scene_name)
                self._last_scene_change_time = time.time()
                logging.debug(
                    "[SceneProcessor] [%s] Scene switched for state '%s' → '%s'",
                    transition.game.name,
                    transition.to_state,
                    scene_name,
                )
            else:
                logging.debug(
                    "[SceneProcessor] [%s] Already on correct scene '%s' for state '%s'",
                    transition.game.name,
                    scene_name,
                    transition.to_state,
                )
        else:
            logging.debug(
                "[SceneProcessor] No scene mapping for %s:%s",
                game_shortname,
                transition.to_state,
            )

    def process_game_change(self, game) -> None:
        """
        Handle game focus change by switching to default scene.

        Args:
            game: New focused game or None if no game focused
        """
        if game is None:
            default_scene = self.settings.get_scene_name("", "Default")
            if default_scene:
                current_scene = self.obs.get_current_scene()
                if current_scene != default_scene:
                    self.obs.set_current_scene(default_scene)
                    self._last_scene_change_time = time.time()
                    logging.debug("[SceneProcessor] Switched to default scene")

    def get_recording_delay_remaining(self) -> float:
        """
        Get remaining delay time before recording can start.

        Returns:
            Remaining delay time in seconds, 0.0 if no delay needed
        """
        if not hasattr(self.settings, "scene_change_delay"):
            return 0.0

        time_since_change = time.time() - self._last_scene_change_time
        remaining = self.settings.scene_change_delay - time_since_change
        return max(0.0, remaining)
