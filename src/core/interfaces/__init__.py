"""
Core interfaces for SIGMArec components.
"""

from .detection import (
    DetectionResult,
    StateTransition,
    IDetectionEngine,
    IGameDetector,
    IStateDetector,
)
from .obs import IOBSController, IOBSEventHandler
from .recording import IRecordingManager, IRecordingStorage

__all__ = [
    "DetectionResult",
    "StateTransition",
    "IDetectionEngine",
    "IGameDetector",
    "IStateDetector",
    "IOBSController",
    "IOBSEventHandler",
    "IRecordingManager",
    "IRecordingStorage",
]
