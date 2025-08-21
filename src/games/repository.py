"""
Game repository implementing the Repository pattern.

This module provides a clean interface for loading and managing games,
separating the concerns of data access from business logic.
"""

import logging
from typing import Dict, List, Optional

from games.objects import Game
from games.objects.factory import GameFactory

from .loader import GameDataError, GameDataLoader


class GameRepository:
    """Repository for loading and managing games."""

    def __init__(self, data_loader: Optional[GameDataLoader] = None):
        """
        Initialize the game repository.

        Args:
            data_loader: Optional game data loader instance (for dependency injection)
        """
        self._data_loader = data_loader or GameDataLoader()
        self._game_factory = GameFactory()
        self._loaded_games: Optional[List[Game]] = None

    def load_all_games(self, force_reload: bool = False) -> List[Game]:
        """
        Load all games from data file.

        Args:
            force_reload: Whether to force reload even if games are cached

        Returns:
            List of all loaded games

        Raises:
            GameDataError: If there's an error loading game data
        """
        if self._loaded_games is not None and not force_reload:
            return self._loaded_games

        games_data = self._data_loader.load_games_data()
        games = []
        errors = []

        for game_name, game_data in games_data.items():
            try:
                self._data_loader.validate_game_data(game_name, game_data)
                game = self._game_factory.create_game(game_name, game_data)
                games.append(game)
            except (GameDataError, ValueError) as e:
                errors.append(f"Failed to load game '{game_name}': {e}")

        if errors:
            for error in errors:
                logging.warning(error)

        self._loaded_games = games
        return games

    def load_game_by_name(self, name: str) -> Game:
        """
        Load a specific game by name.

        Args:
            name: Name of the game to load

        Returns:
            The loaded game

        Raises:
            GameDataError: If game not found or invalid
        """
        game_data = self._data_loader.get_game_data(name)
        return self._game_factory.create_game(name, game_data)

    def get_game_names(self) -> List[str]:
        """Get a list of all available game names."""
        return self._data_loader.get_game_names()

    def find_games_by_type(self, game_type: str) -> List[Game]:
        """
        Find all games of a specific type.

        Args:
            game_type: Type of games to find (e.g., 'pixel', 'log')

        Returns:
            List of games of the specified type
        """
        all_games = self.load_all_games()
        return [game for game in all_games if game.game_type.value == game_type]

    def find_games_by_process(self, process_name: str) -> List[Game]:
        """
        Find all games that monitor a specific process.

        Args:
            process_name: Name of the process to search for

        Returns:
            List of games that monitor the specified process
        """
        all_games = self.load_all_games()
        matching_games = []

        for game in all_games:
            for process_info in game.processes:
                if process_info.matches_process(process_name):
                    matching_games.append(game)
                    break

        return matching_games

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about loaded games.

        Returns:
            Dictionary with game statistics
        """
        games = self.load_all_games()

        stats = {
            "total_games": len(games),
            "pixel_games": len([g for g in games if g.game_type.value == "pixel"]),
            "log_games": len([g for g in games if g.game_type.value == "log"]),
            "total_patterns": len(
                [g for g in games for s in g.states.values() for p in s.patterns]
            ),
        }

        return stats
