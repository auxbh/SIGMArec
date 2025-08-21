"""
Game data loading and validation.

This module handles loading game definition files and provides clean interfaces
for accessing game data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from games.objects.types import GameType


class GameDataError(Exception):
    """Raised when there's an error with game data loading or validation."""


class GameDataLoader:
    """Handles loading and comprehensive validation of game definition files."""

    def __init__(self, games_data_path: str = "games.json"):
        """
        Initialize the game data loader.

        Args:
            games_data_path: Path to the games definition file
        """
        self.games_data_path = Path(games_data_path)

    def load_games_data(self) -> Dict[str, Any]:
        """
        Load the games data from file.

        Returns:
            Dict containing all game definitions

        Raises:
            GameDataError: If file doesn't exist or can't be parsed
        """
        if not self.games_data_path.exists():
            raise GameDataError(f"Game data file not found: {self.games_data_path}")

        try:
            with open(self.games_data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise GameDataError(f"Invalid JSON in game data file: {e}") from e
        except Exception as e:
            raise GameDataError(f"Error reading game data file: {e}") from e

    def validate_game_data(self, name: str, game_data: Dict[str, Any]) -> None:
        """
        Validate a single game definition comprehensively.

        Args:
            name: Name of the game
            game_data: Game definition dictionary

        Raises:
            GameDataError: If game data is invalid
        """
        self._validate_required_fields(name, game_data)
        self._validate_game_type(name, game_data)
        self._validate_processes(name, game_data)
        self._validate_states(name, game_data)

    def get_game_names(self) -> List[str]:
        """Get a list of all game names in the data file."""
        data = self.load_games_data()
        return list(data.keys())

    def get_game_data(self, name: str) -> Dict[str, Any]:
        """
        Get data for a specific game.

        Args:
            name: Name of the game

        Returns:
            Game definition dictionary

        Raises:
            GameDataError: If game not found
        """
        data = self.load_games_data()

        if name not in data:
            available_games = ", ".join(data.keys())
            raise GameDataError(
                f"Game '{name}' not found. Available games: {available_games}"
            )

        game_data = data[name]
        self.validate_game_data(name, game_data)
        return game_data

    def _validate_required_fields(self, name: str, game_data: Dict[str, Any]) -> None:
        """Validate that all required fields are present."""
        required_fields = ["type", "processes", "states"]

        for field in required_fields:
            if field not in game_data:
                raise GameDataError(f"Game '{name}' missing required field: '{field}'")

    def _validate_game_type(self, name: str, game_data: Dict[str, Any]) -> None:
        """Validate the game type field."""
        game_type = game_data.get("type")
        valid_types = [t.value for t in GameType]

        if game_type not in valid_types:
            raise GameDataError(
                f"Game '{name}' has invalid type '{game_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            )

    def _validate_processes(self, name: str, game_data: Dict[str, Any]) -> None:
        """Validate the processes field."""
        processes = game_data.get("processes", [])

        if not isinstance(processes, list):
            raise GameDataError(
                f"Game '{name}' processes must be a list, got {type(processes).__name__}"
            )

        if not processes:
            raise GameDataError(f"Game '{name}' must have at least one process")

        for i, process in enumerate(processes):
            self._validate_process(name, i, process)

    def _validate_process(
        self, game_name: str, process_index: int, process: Dict[str, Any]
    ) -> None:
        """Validate a single process definition."""
        if not isinstance(process, dict):
            raise GameDataError(
                f"Game '{game_name}' process {process_index} must be a dictionary, "
                f"got {type(process).__name__}"
            )

        if "exe" not in process and "title" not in process:
            raise GameDataError(
                f"Game '{game_name}' process {process_index} must have 'exe' or 'title'"
            )

        if "exe" in process and not isinstance(process["exe"], str):
            raise GameDataError(
                f"Game '{game_name}' process {process_index} 'exe' must be a string"
            )

        if "title" in process and not isinstance(process["title"], str):
            raise GameDataError(
                f"Game '{game_name}' process {process_index} 'title' must be a string"
            )

    def _validate_states(self, name: str, game_data: Dict[str, Any]) -> None:
        """Validate the states field."""
        states = game_data.get("states", {})

        if not isinstance(states, dict):
            raise GameDataError(
                f"Game '{name}' states must be a dictionary, got {type(states).__name__}"
            )

        if not states:
            raise GameDataError(f"Game '{name}' must have at least one state")

        game_type = game_data.get("type")

        for state_name, state_data in states.items():
            if not isinstance(state_name, str):
                raise GameDataError(
                    f"Game '{name}' state name must be a string, got {type(state_name).__name__}"
                )

            self._validate_state(name, state_name, state_data, game_type)

    def _validate_state(
        self,
        game_name: str,
        state_name: str,
        state_data: Dict[str, Any],
        game_type: str,
    ) -> None:
        """Validate a single state definition."""
        if "patterns" not in state_data:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' missing required field 'patterns'"
            )

        patterns = state_data.get("patterns", [])
        if not isinstance(patterns, list):
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' patterns must be a list, "
                f"got {type(patterns).__name__}"
            )

        if not patterns:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' must have at least one pattern"
            )

        for i, pattern in enumerate(patterns):
            self._validate_pattern(game_name, state_name, i, pattern, game_type)

    def _validate_pattern(
        self,
        game_name: str,
        state_name: str,
        pattern_index: int,
        pattern_data: Dict[str, Any],
        game_type: str,
    ) -> None:
        """Validate a single pattern definition."""
        if game_type == GameType.PIXEL.value:
            self._validate_pixel_pattern(
                game_name, state_name, pattern_index, pattern_data
            )
        elif game_type == GameType.LOG.value:
            self._validate_log_pattern(
                game_name, state_name, pattern_index, pattern_data
            )
        else:
            raise GameDataError(
                f"Game '{game_name}' has unsupported game type '{game_type}' for pattern validation"
            )

    def _validate_pixel_pattern(
        self,
        game_name: str,
        state_name: str,
        pattern_index: int,
        pattern_data: Dict[str, Any],
    ) -> None:
        """Validate a pixel pattern definition."""
        if "pixels" not in pattern_data:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"missing required field 'pixels'"
            )

        pixels = pattern_data.get("pixels", [])
        if not isinstance(pixels, list):
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"'pixels' must be a list, got {type(pixels).__name__}"
            )

        if not pixels:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"must have at least one pixel"
            )

        if "resolution" in pattern_data:
            resolution = pattern_data["resolution"]
            if not isinstance(resolution, list) or len(resolution) != 2:
                raise GameDataError(
                    f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                    f"'resolution' must be a list with 2 integers [width, height]"
                )

            if not all(isinstance(x, int) and x > 0 for x in resolution):
                raise GameDataError(
                    f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                    f"'resolution' values must be positive integers"
                )

        for i, pixel_data in enumerate(pixels):
            self._validate_pixel(game_name, state_name, pattern_index, i, pixel_data)

    def _validate_pixel(
        self,
        game_name: str,
        state_name: str,
        pattern_index: int,
        pixel_index: int,
        pixel_data: List,
    ) -> None:
        """Validate a single pixel definition."""
        if len(pixel_data) < 6:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"pixel {pixel_index} must have at least 6 elements [x, y, r, g, b, tolerance], "
                f"got {len(pixel_data)}"
            )

        x, y, r, g, b, tolerance = pixel_data[:6]

        if not isinstance(x, int) or x < 0:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"pixel {pixel_index} x coordinate must be a non-negative integer, got {x}"
            )

        if not isinstance(y, int) or y < 0:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"pixel {pixel_index} y coordinate must be a non-negative integer, got {y}"
            )

        for color_name, color_value in [("r", r), ("g", g), ("b", b)]:
            if not isinstance(color_value, int) or not 0 <= color_value <= 255:
                raise GameDataError(
                    f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                    f"pixel {pixel_index} {color_name} must be an integer 0-255, got {color_value}"
                )

        if not isinstance(tolerance, int) or tolerance < 0:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"pixel {pixel_index} tolerance must be a non-negative integer, got {tolerance}"
            )

    def _validate_log_pattern(
        self,
        game_name: str,
        state_name: str,
        pattern_index: int,
        pattern_data: Dict[str, Any],
    ) -> None:
        """Validate a log pattern definition."""
        if "class" not in pattern_data and "method" not in pattern_data:
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"must have at least one of 'class' or 'method' fields"
            )

        if "class" in pattern_data and not isinstance(pattern_data["class"], str):
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"'class' must be a string, got {type(pattern_data['class']).__name__}"
            )

        if "method" in pattern_data and not isinstance(pattern_data["method"], str):
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"'method' must be a string, got {type(pattern_data['method']).__name__}"
            )

        if "description" in pattern_data and not isinstance(
            pattern_data["description"], str
        ):
            raise GameDataError(
                f"Game '{game_name}' state '{state_name}' pattern {pattern_index} "
                f"'description' must be a string, got {type(pattern_data['description']).__name__}"
            )
