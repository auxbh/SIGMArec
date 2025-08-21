"""
Detection engine package for SIGMArec.

This package contains the core detection logic that bridges game state detection
with OBS recording control.
"""

from .engine import DetectionEngine
from .log_service import LogService
from .process_monitor import ProcessMonitor
from .screen_capture import ScreenCaptureService
from .state_machine import StateMachine, TransitionPattern

__all__ = [
    "DetectionEngine",
    "ScreenCaptureService",
    "ProcessMonitor",
    "LogService",
    "StateMachine",
    "TransitionPattern",
]
