"""
Game management package for SIGMArec.

Contains game data loading, validation, and repository management.
"""

from .loader import GameDataError, GameDataLoader
from .objects import (
    Game,
    GameFactory,
    GameType,
    LogGame,
    LogPattern,
    LogState,
    Pattern,
    Pixel,
    PixelGame,
    PixelPattern,
    PixelState,
    ProcessFactory,
    ProcessInfo,
    State,
)
from .repository import GameRepository

__all__ = [
    "GameDataError",
    "GameDataLoader",
    "Game",
    "GameFactory",
    "GameType",
    "LogGame",
    "LogPattern",
    "LogState",
    "Pattern",
    "Pixel",
    "PixelGame",
    "PixelPattern",
    "PixelState",
    "ProcessFactory",
    "ProcessInfo",
    "State",
    "GameRepository",
]
