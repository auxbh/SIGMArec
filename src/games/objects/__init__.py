"""
Game objects package for SIGMArec.

Contains the core game objects that define the structure and behavior of games.
"""

from .base import Game, Pattern, State
from .games import LogGame, PixelGame
from .log import LogPattern, LogState
from .pixel import Pixel, PixelPattern, PixelState
from .process import ProcessInfo
from .factory import GameFactory, ProcessFactory

__all__ = [
    "Pattern",
    "State",
    "Game",
    "ProcessInfo",
    "Pixel",
    "PixelPattern",
    "PixelState",
    "LogPattern",
    "LogState",
    "LogGame",
    "PixelGame",
    "GameFactory",
    "ProcessFactory",
]
