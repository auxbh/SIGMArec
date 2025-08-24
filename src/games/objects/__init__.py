"""
Game objects package for SIGMArec.

Contains the core game objects that define the structure and behavior of games.
"""

from .base import Game, Pattern, State
from .factory import GameFactory, ProcessFactory
from .games import LogGame, PixelGame
from .log import LogPattern, LogState
from .pixel import Pixel, PixelPattern, PixelState
from .process import ProcessInfo
from .types import GameType

__all__ = [
    "Game",
    "Pattern",
    "State",
    "GameFactory",
    "ProcessFactory",
    "LogGame",
    "PixelGame",
    "LogPattern",
    "LogState",
    "Pixel",
    "PixelPattern",
    "PixelState",
    "ProcessInfo",
    "GameType",
]
