"""
Lightweight state machine with history and transition pattern matching.

This module provides a small, focused state machine that tracks a bounded
history of confirmed states and detects when certain transition sequences
occur (e.g., ["Playing", "Unknown", "Playing"], ["*", "Unknown"]).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

WILDCARD = "*"


@dataclass(frozen=True)
class TransitionPattern:
    """
    A named transition pattern that will be matched against the trailing
    slice of the state history.

    The sequence may contain the wildcard token "*" which matches any single
    state.
    """

    name: str
    sequence: Tuple[str, ...]


class StateMachine:
    """
    Simple state machine with bounded history and pattern detection.

    Usage:
      sm = StateMachine(max_history=10)
      sm.add_pattern(TransitionPattern("restart", ("Playing", "Unknown", "Playing")))
      sm.push_state("Playing")
      matches = sm.get_last_matches()
    """

    def __init__(self, max_history: int = 10):
        self._max_history: int = max(2, max_history)
        self._history: List[str] = []
        self._patterns: List[TransitionPattern] = []
        self._last_matches: List[str] = []

    @property
    def history(self) -> List[str]:
        """Get the state history."""
        return list(self._history)

    @property
    def current_state(self) -> Optional[str]:
        """Get the current state."""
        return self._history[-1] if self._history else None

    @property
    def previous_state(self) -> Optional[str]:
        """Get the previous state."""
        return self._history[-2] if len(self._history) >= 2 else None

    def clear(self) -> None:
        """Clear the state machine history."""
        self._history.clear()
        self._last_matches = []

    def add_pattern(self, pattern: TransitionPattern) -> None:
        """Add a single pattern."""
        if not pattern.sequence:
            return
        self._patterns.append(pattern)

    def add_patterns(self, patterns: Sequence[TransitionPattern]) -> None:
        """Add multiple patterns at once."""
        for p in patterns:
            self.add_pattern(p)

    def push_state(self, new_state: str) -> None:
        """
        Push a new confirmed state change into the history.
        Consecutive duplicates are ignored.
        """
        if self._history and self._history[-1] == new_state:
            self._last_matches = []
            return

        self._history.append(new_state)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        self._last_matches = self._match_tail_patterns()

    def get_last_matches(self) -> List[str]:
        """Return pattern names that matched when the most recent state was pushed."""
        return list(self._last_matches)

    def _match_tail_patterns(self) -> List[str]:
        matches: List[str] = []
        for pattern in self._patterns:
            if self._history_ends_with(pattern.sequence):
                matches.append(pattern.name)
        return matches

    def _history_ends_with(self, sequence: Tuple[str, ...]) -> bool:
        seq_len = len(sequence)
        if len(self._history) < seq_len:
            return False
        start_index = len(self._history) - seq_len
        for i, token in enumerate(sequence):
            state_value = self._history[start_index + i]
            if token != WILDCARD and token != state_value:
                return False
        return True
