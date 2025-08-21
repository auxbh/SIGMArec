"""
OBS module for SIGMArec.

Provides OBS WebSocket API wrapper and recording manager.
"""

from .controller import OBSController
from .manager import Recording

__all__ = ["OBSController", "Recording"]
