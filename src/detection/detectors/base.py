"""
Base state detector implementation.
"""

from abc import abstractmethod
from typing import Optional

from src.core.interfaces import IStateDetector
from src.games import Game


class BaseStateDetector(IStateDetector):
    """Base implementation for state detectors."""

    def __init__(self, detection_threshold: int = 2):
        """
        Initialize base detector.

        Args:
            detection_threshold: Number of consecutive detections required
        """
        self.detection_threshold = detection_threshold
        self._consecutive_detections = 0
        self._last_detected_state: Optional[str] = None

    def detect_state(self, game: Game) -> Optional[str]:
        """
        Detect state with confirmation threshold.

        Args:
            game: Game to detect state for

        Returns:
            Confirmed state or None if not enough confirmations
        """
        raw_state = self._detect_raw_state(game)

        if raw_state != self._last_detected_state:
            self._last_detected_state = raw_state
            self._consecutive_detections = 1
        else:
            self._consecutive_detections += 1

        if self._consecutive_detections >= self.detection_threshold:
            return raw_state

        return None

    @abstractmethod
    def _detect_raw_state(self, game: Game) -> Optional[str]:
        """Detect state without confirmation threshold."""

    def reset_detection_state(self) -> None:
        """Reset detection counters."""
        self._consecutive_detections = 0
        self._last_detected_state = None
