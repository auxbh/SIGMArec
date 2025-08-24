"""
Handles OBS scene switching based on game states.
"""

import logging

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
            self.obs.set_current_scene(scene_name)
            logging.debug(
                "[SceneProcessor] [%s] Scene switched for state '%s' → '%s'",
                transition.game.name,
                transition.to_state,
                scene_name,
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
                self.obs.set_current_scene(default_scene)
                logging.debug("[SceneProcessor] Switched to default scene")
