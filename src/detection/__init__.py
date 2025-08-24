"""
Detection engine package for SIGMArec.

This package contains the core detection logic that bridges game state detection
with OBS recording control.
"""

from .detectors import (
    BaseStateDetector,
    GameDetector,
    LogStateDetector,
    PixelStateDetector,
)
from .engine import DetectionCoordinator, StateManager
from .log_service import LogService
from .process_monitor import ProcessMonitor
from .processors import RecordingProcessor, SceneProcessor
from .screen_capture import ScreenCaptureService
from .state_machine import StateMachine, TransitionPattern

__all__ = [
    "BaseStateDetector",
    "GameDetector",
    "LogStateDetector",
    "PixelStateDetector",
    "DetectionCoordinator",
    "StateManager",
    "LogService",
    "ProcessMonitor",
    "RecordingProcessor",
    "SceneProcessor",
    "ScreenCaptureService",
    "StateMachine",
    "TransitionPattern",
]
