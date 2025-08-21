"""
Factory classes for creating SIGMArec objects from configuration.

This module implements the Factory pattern to create games and related objects
from configuration data, following proper separation of concerns.
"""

from typing import Any, Dict, List

from .base import Game
from .games import LogGame, PixelGame
from .process import ProcessInfo
from .types import GameType


class ProcessFactory:
    """Factory for creating ProcessInfo objects."""

    @staticmethod
    def create_from_config(process_config: Dict[str, Any]) -> ProcessInfo:
        """Create a ProcessInfo from configuration data."""
        return ProcessInfo(
            exe=process_config.get("exe", ""), title=process_config.get("title", "")
        )

    @staticmethod
    def create_list_from_config(
        processes_config: List[Dict[str, Any]],
    ) -> List[ProcessInfo]:
        """Create a list of ProcessInfo objects from configuration data."""
        return [
            ProcessFactory.create_from_config(proc_config)
            for proc_config in processes_config
        ]


class GameFactory:
    """Factory for creating Game objects from configuration."""

    _game_types = {GameType.LOG.value: LogGame, GameType.PIXEL.value: PixelGame}

    @classmethod
    def create_game(cls, name: str, config: Dict[str, Any]) -> Game:
        """
        Create a Game object from configuration data.

        Args:
            name: The name of the game
            config: Configuration dictionary for the game

        Returns:
            Game: The created game object

        Raises:
            ValueError: If game type is not supported
        """
        game_type = config.get("type")

        if game_type not in cls._game_types:
            supported_types = ", ".join(cls._game_types.keys())
            raise ValueError(
                f"Unsupported game type '{game_type}'. "
                f"Supported types: {supported_types}"
            )

        game_class = cls._game_types[game_type]
        return game_class.from_config(name, config)

    @classmethod
    def register_game_type(cls, game_type: str, game_class: type) -> None:
        """
        Register a new game type for the factory.

        This allows extending the factory with new game types without
        modifying the core factory code (Open/Closed Principle).
        """
        cls._game_types[game_type] = game_class

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get a list of all supported game types."""
        return list(cls._game_types.keys())
