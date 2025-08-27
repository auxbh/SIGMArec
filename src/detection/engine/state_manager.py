"""
Manages game state transitions and pattern matching.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from src.core.interfaces import StateTransition
from src.detection.log_service import LogService
from src.detection.state_machine import StateMachine, TransitionPattern
from src.games import Game, LogGame


@dataclass
class StateContext:
    """Context information for state management."""

    current_game: Optional[Game] = None
    current_state: Optional[str] = None
    previous_state: Optional[str] = None
    last_playing_timestamp: Optional[str] = None
    machine: StateMachine = field(default_factory=lambda: StateMachine(max_history=3))


class StateManager:
    """Manages state transitions and pattern matching for games."""

    def __init__(self):
        """Initialize state manager."""
        self.context = StateContext()
        self.logs = LogService()

        self._setup_transition_patterns()

    def update_game(self, game: Optional[Game]) -> Optional[StateTransition]:
        """
        Update the current game context.

        Args:
            game: New active game or None if no game active

        Returns:
            StateTransition if game changed, None otherwise
        """
        if game == self.context.current_game:
            return None

        previous_game = self.context.current_game

        self.context.current_game = game
        self.context.current_state = None
        self.context.previous_state = None
        self.context.last_playing_timestamp = None
        self.context.machine.clear()

        if previous_game:
            if game:
                logging.info("Tabbed into %s", game.name)
            else:
                logging.info("Tabbed out of %s", previous_game.name)
        elif game:
            logging.info("Tabbed into %s", game.name)

        return None

    def update_state(self, new_state: Optional[str]) -> Optional[StateTransition]:
        """
        Update the current state and check for transitions.

        Args:
            new_state: New detected state

        Returns:
            StateTransition if valid transition occurred, None otherwise
        """
        if not self.context.current_game:
            return None

        # Handle LogGame Playing → Playing transitions (BMS quick restarts)
        if (
            self.context.current_state == "Playing"
            and new_state == "Playing"
            and isinstance(self.context.current_game, LogGame)
        ):
            if self._should_restart_for_timestamp_change():
                logging.debug(
                    "[StateManager] Timestamp change detected, triggering restart"
                )

                # Create a restart transition directly without relying on state machine
                # pattern matching since the state machine ignores consecutive duplicates
                self.context.machine.push_state(new_state)
                transition = StateTransition(
                    from_state=self.context.current_state,
                    to_state=new_state,
                    game=self.context.current_game,
                    timestamp=time.time(),
                    triggered_patterns=["restart"],
                )
                self.context.previous_state = self.context.current_state
                self.context.current_state = new_state

                # Update the playing timestamp to prevent detecting the same change again
                self._update_playing_timestamp()

                return transition

        # Normal state transition handling
        if new_state and new_state != self.context.current_state:
            self.context.machine.push_state(new_state)
            return self._create_transition(new_state)

        return None

    def get_current_state(self) -> Optional[str]:
        """Get the current confirmed state."""
        return self.context.current_state

    def get_current_game(self) -> Optional[Game]:
        """Get the current active game."""
        return self.context.current_game

    def clear_context(self) -> None:
        """Clear all state context."""
        self.context = StateContext()
        self._setup_transition_patterns()

    def _create_transition(self, new_state: str) -> StateTransition:
        """
        Create a state transition object.

        Args:
            new_state: The new state being transitioned to

        Returns:
            StateTransition object
        """
        if new_state == "Playing" and isinstance(self.context.current_game, LogGame):
            self._update_playing_timestamp()

        patterns = self.context.machine.get_last_matches()

        transition = StateTransition(
            from_state=self.context.current_state,
            to_state=new_state,
            game=self.context.current_game,
            timestamp=time.time(),
            triggered_patterns=patterns,
        )

        self.context.previous_state = self.context.current_state
        self.context.current_state = new_state

        return transition

    def _setup_transition_patterns(self) -> None:
        """Setup state machine transition patterns."""
        patterns = [
            TransitionPattern("start_play", ("Select", "Playing")),
            TransitionPattern("start_play", ("Select", "Unknown", "Playing")),
            TransitionPattern("start_play", ("Result", "Unknown", "Playing")),
            TransitionPattern("discard_play", ("Playing", "Select")),
            TransitionPattern("discard_play", ("Playing", "Unknown", "Select")),
            TransitionPattern("stop_play", ("Playing", "Result")),
            TransitionPattern("stop_play", ("Playing", "Unknown", "Result")),
            TransitionPattern("restart", ("Playing", "Unknown", "Playing")),
            TransitionPattern("restart", ("Playing", "Playing")),
        ]

        self.context.machine.add_patterns(patterns)

    def _should_restart_for_timestamp_change(self) -> bool:
        """
        Check if Playing → Playing transition should trigger restart.
        Only applicable for LogGame types.
        """
        if not isinstance(self.context.current_game, LogGame):
            return False

        entries = self.logs.get_log_entries_for_game(
            self.context.current_game.name, self.context.current_game.logs
        )

        if not entries:
            return False

        current_timestamp = self.context.current_game.get_playing_state_timestamp(
            entries
        )
        if not current_timestamp:
            return False

        if self.context.last_playing_timestamp is None:
            return False

        should_restart = current_timestamp != self.context.last_playing_timestamp
        if should_restart:
            logging.debug(
                "[StateManager] Timestamp change: %s → %s",
                self.context.last_playing_timestamp,
                current_timestamp,
            )

        return should_restart

    def _update_playing_timestamp(self) -> None:
        """Update stored Playing timestamp for LogGame."""
        if not isinstance(self.context.current_game, LogGame):
            return

        entries = self.logs.get_log_entries_for_game(
            self.context.current_game.name, self.context.current_game.logs
        )

        if not entries:
            return

        current_timestamp = self.context.current_game.get_playing_state_timestamp(
            entries
        )
        if current_timestamp:
            self.context.last_playing_timestamp = current_timestamp
