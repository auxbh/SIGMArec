"""
Detection engine rewritten from scratch to use the centralized StateMachine.

Rules implemented:
- Start: Select → (Unknown optional) → Playing OR Unknown → Playing
- Stop+Delete: Playing → (Unknown optional) → Select OR Playing → Unknown
- Stop+Save (after delay): Playing → (Unknown optional) → Result
- Restart: Playing → Unknown → Playing (stop, discard, then start)
- LogGame Restart: Playing → Playing (with different timestamp, stop, discard, then start)
"""

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
import win32gui
import win32process

from audio import SoundService
from config.settings import AppSettings
from games.objects import Game, LogGame, PixelGame, ProcessInfo
from obs import OBSController, Recording

from .log_service import LogService
from .process_monitor import ProcessMonitor
from .screen_capture import ScreenCaptureService
from .state_machine import StateMachine, TransitionPattern


@dataclass
class DetectionState:
    """Runtime state for the detection engine."""

    current_game: Optional[Game] = None
    current_state: Optional[str] = None
    previous_state: Optional[str] = None
    last_seen_detection: Optional[str] = None
    consecutive_detections: int = 0
    recording_active: bool = False
    last_detection_time: float = 0.0
    last_playing_timestamp: Optional[str] = None
    machine: StateMachine = field(default_factory=lambda: StateMachine(max_history=3))


class DetectionEngine:
    """Coordinates game detection and OBS recording using a StateMachine."""

    def __init__(
        self, obs_controller: OBSController, games: List[Game], settings: AppSettings
    ):
        self.obs = obs_controller
        self.games = games
        self.settings = settings

        self.screen = ScreenCaptureService()
        self.procmon = ProcessMonitor()
        self.logs = LogService()
        self.recording_manager = Recording(settings)
        self.sound_service = SoundService(settings)

        self.state = DetectionState()
        self._delete_next_recording: bool = False
        self._restart_after_stop: bool = False

        # Transition patterns
        self.state.machine.add_patterns(
            [
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
        )

        logging.info("[Detection] Engine ready with %s games", len(self.games))

    # Public API
    def detect_and_control(self) -> Dict[str, Any]:
        """Detect the current game state and control the recording process."""
        now = time.time()
        game = self._active_game()

        if game is None:
            self._on_no_active_game()
            return {"game": None, "state": None, "action": "idle"}

        if game is not self.state.current_game:
            self._on_game_changed(game)

        detected = self._detect_state_for(game)

        # Special case: check for recent playing patterns when already in playing state
        if (
            self.state.current_state == "Playing"
            and isinstance(game, LogGame)
            and self.state.recording_active
            and self._has_recent_playing_pattern()
        ):
            logging.info(
                "[Detection] Quick restart detected - stopping current recording"
            )
            # Stop the current recording and mark it for deletion
            # The new recording will be started when the old one completes
            self._delete_next_recording = True
            self._restart_after_stop = True  # Flag to start new recording after stop
            self._stop_recording(immediate=True)
            # Update the playing timestamp to reflect the new session
            self._update_playing_timestamp()
            return {
                "game": self.state.current_game.name
                if self.state.current_game
                else None,
                "state": self.state.current_state,
                "detected": detected,
                "recording_active": self.state.recording_active,
                "consecutive": self.state.consecutive_detections,
                "timestamp": now,
                "action": "restart_stopping",
            }

        self._update_detection_counters(detected)
        self._maybe_confirm_state(detected)

        self.state.last_detection_time = now
        return {
            "game": self.state.current_game.name if self.state.current_game else None,
            "state": self.state.current_state,
            "detected": detected,
            "recording_active": self.state.recording_active,
            "consecutive": self.state.consecutive_detections,
            "timestamp": now,
        }

    def handle_recording_completed(self, output_path: str) -> None:
        """Handle the completion of a recording."""

        def _handle_recording_in_thread():
            if self._delete_next_recording:
                self._delete_recording(output_path)
            else:
                self._finalize_recording(output_path)

        threading.Thread(target=_handle_recording_in_thread, daemon=True).start()

        self._delete_next_recording = False

        # Check if we need to start a new recording after this one stopped
        if self._restart_after_stop:
            logging.info("[Detection] Starting new recording after restart")
            self._restart_after_stop = False
            self._start_recording()

    def can_save_lastplay(self) -> bool:
        """Check if the last play can be saved."""
        if self.state.recording_active:
            return False
        if not self.recording_manager.has_lastplay():
            return False
        return self.state.current_state in [None, "Select", "Result"]

    def save_current_lastplay(self) -> Tuple[bool, str]:
        """Save the current last play."""
        return self.recording_manager.save_lastplay(self.state.current_game)

    def get_current_status(self) -> Dict[str, Any]:
        """Get the current status of the detection engine."""
        return {
            "current_game": self.state.current_game.name
            if self.state.current_game
            else None,
            "current_state": self.state.current_state,
            "consecutive_detections": self.state.consecutive_detections,
            "recording_active": self.state.recording_active,
            "last_detection": self.state.last_detection_time,
            "games_loaded": len(self.games),
            "focused_window": self.screen.get_focused_window_title(),
        }

    # Detection
    def _active_game(self) -> Optional[Game]:
        title = self.screen.get_focused_window_title()
        if not title:
            return None

        # Try log-based games first when a Java window is foreground
        if self._foreground_is_java():
            for g in self.games:
                if isinstance(g, LogGame) and self._matches_focused(g, title):
                    return g

        # Then pixel-based games
        for g in self.games:
            if isinstance(g, PixelGame) and self._matches_focused(g, title):
                return g

        return None

    def _foreground_is_java(self) -> bool:
        return self.logs.get_foreground_java_process_info() is not None

    def _matches_focused(self, game: Game, window_title: str) -> bool:
        process_name = self._focused_process_name()
        if not process_name:
            return False
        for p in game.processes:
            if isinstance(p, ProcessInfo) and p.matches_process(
                process_name, window_title
            ):
                return True
        return False

    def _focused_process_name(self) -> Optional[str]:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()

    def _detect_state_for(self, game: Game) -> Optional[str]:
        if isinstance(game, PixelGame):
            shot = self.screen.capture_focused_window()
            if not shot:
                return None
            state_obj = game.get_current_state(shot)
            return state_obj.get_name() if state_obj else None
        if isinstance(game, LogGame):
            entries = self.logs.get_log_entries_for_game(game.name, game.logs)
            if not entries:
                return None
            state_obj = game.get_current_state(entries)
            return state_obj.get_name() if state_obj else None
        return None

    # State confirmation and control
    def _update_detection_counters(self, detected: Optional[str]) -> None:
        if detected != self.state.last_seen_detection:
            self.state.last_seen_detection = detected
            # Pixel games: consider None as Unknown for streak counting
            if detected is None and isinstance(self.state.current_game, PixelGame):
                self.state.consecutive_detections = 1
            elif detected is None:
                self.state.consecutive_detections = 0
            else:
                self.state.consecutive_detections = 1
        else:
            if detected or isinstance(self.state.current_game, PixelGame):
                self.state.consecutive_detections += 1

    def _maybe_confirm_state(self, detected: Optional[str]) -> None:
        if self.state.consecutive_detections < self.settings.detections_required:
            return

        # Pixel games: convert repeated None to confirmed Unknown
        if detected is None and isinstance(self.state.current_game, PixelGame):
            if self.state.current_state != "Unknown":
                self._confirm_state("Unknown")
        elif detected and detected != self.state.current_state:
            self._confirm_state(detected)

    def _confirm_state(self, new_state: str) -> None:
        prev = self.state.current_state

        # Special handling for LogGame Playing to Playing transitions
        if (
            prev == "Playing"
            and new_state == "Playing"
            and isinstance(self.state.current_game, LogGame)
        ):
            # Check if this is a different Playing session by comparing timestamps
            if self._should_restart_for_timestamp_change():
                # Force the transition pattern by pushing Playing again
                self.state.machine.push_state(new_state)
                self.state.previous_state = prev
                self.state.current_state = new_state
                self._on_state_committed()
                return

        self.state.machine.push_state(new_state)
        self.state.previous_state = prev
        self.state.current_state = new_state
        self._on_state_committed()

    def _on_state_committed(self) -> None:
        game_name = self.state.current_game.name if self.state.current_game else "?"
        prev = self.state.previous_state
        curr = self.state.current_state
        if prev:
            logging.info("[Detection] [%s] %s → %s", game_name, prev, curr)
        else:
            logging.info("[Detection] [%s] %s", game_name, curr)

        # Handle scene switching when state changes
        if curr and prev != curr:
            self._handle_scene_switching(curr)

        # Update Playing timestamp for LogGame
        if curr == "Playing" and isinstance(self.state.current_game, LogGame):
            self._update_playing_timestamp()

        matches = set(self.state.machine.get_last_matches())

        # Restart takes precedence when already recording
        if ("restart" in matches) and self.state.recording_active:
            logging.info("[Detection] Play restarted")
            self._delete_next_recording = True
            self._restart_after_stop = True
            self._stop_recording(immediate=True)
            return

        # Start recording sequences
        if ("start_play" in matches) and not self.state.recording_active:
            self._start_recording()
            return

        # Stop and delete sequences
        if ("discard_play" in matches) and self.state.recording_active:
            self._delete_next_recording = True
            self._restart_after_stop = False
            self._stop_recording(immediate=True, playfailed=True)
            return

        # Stop and save (after delay)
        if "stop_play" in matches and self.state.recording_active:
            self._stop_recording(immediate=False)
            return

    # Recording controls
    def _start_recording(self, playsound: bool = True) -> None:
        logging.info("[Detection] Start recording")
        if playsound:
            self.sound_service.play_start()
        self.obs.start_recording()
        self.state.recording_active = True

    def _stop_recording(self, immediate: bool, playfailed: bool = False) -> None:
        if not immediate:
            logging.info(
                "[Detection] Waiting %ss before stopping", self.settings.result_wait
            )
            time.sleep(self.settings.result_wait)
        if playfailed:
            self.sound_service.play_failed()
        self.obs.stop_recording()
        self.state.recording_active = False

    # Active game changes / loss of focus
    def _on_game_changed(self, game: Game) -> None:
        logging.info("[Detection] Focused game: %s", game.name)
        self.state.current_game = game
        self.state.consecutive_detections = 0
        self.state.last_seen_detection = None
        self.state.machine.clear()
        self.state.current_state = None
        self.state.previous_state = None
        self.state.last_playing_timestamp = None
        self._restart_after_stop = False

    def _on_no_active_game(self) -> None:
        if self.state.current_game is None:
            return
        logging.info("[Detection] No active game window")

        # Switch to default scene if configured
        default_scene = self.settings.get_scene_name("", "Default")
        if default_scene:
            logging.info("[Detection] Switching to default scene '%s'", default_scene)
            self.obs.set_current_scene(default_scene)

        self.state.current_game = None
        self.state.consecutive_detections = 0
        self.state.last_seen_detection = None
        self.state.machine.clear()
        self.state.current_state = None
        self.state.previous_state = None
        self.state.last_playing_timestamp = None
        self._restart_after_stop = False
        if self.state.recording_active:
            # Losing focus discards the take
            self._delete_next_recording = True
            self._stop_recording(immediate=True)

    # LogGame timestamp handling helpers
    def _should_restart_for_timestamp_change(self) -> bool:
        """
        Check if a Playing to Playing transition should trigger a restart
        based on timestamp differences in LogGame.
        """
        if not isinstance(self.state.current_game, LogGame):
            return False

        # Get the current Playing timestamp from log entries
        entries = self.logs.get_log_entries_for_game(
            self.state.current_game.name, self.state.current_game.logs
        )
        if not entries:
            return False

        current_timestamp = self.state.current_game.get_playing_state_timestamp(entries)
        if not current_timestamp:
            return False

        # Compare with stored timestamp
        if self.state.last_playing_timestamp is None:
            return False

        # If timestamps are different, this is a new Playing session
        return current_timestamp != self.state.last_playing_timestamp

    def _update_playing_timestamp(self) -> None:
        """Update the stored Playing timestamp for LogGame."""
        if not isinstance(self.state.current_game, LogGame):
            return

        entries = self.logs.get_log_entries_for_game(
            self.state.current_game.name, self.state.current_game.logs
        )
        if not entries:
            return

        current_timestamp = self.state.current_game.get_playing_state_timestamp(entries)
        if current_timestamp:
            self.state.last_playing_timestamp = current_timestamp

    def _has_recent_playing_pattern(self) -> bool:
        """
        Check if there are recent playing patterns in the log file that are newer
        than our current playing session.
        """
        if not isinstance(self.state.current_game, LogGame):
            return False

        playing_state = self.state.current_game.states.get("Playing")
        if not playing_state:
            return False

        # Use the last playing timestamp as the cutoff
        return self.logs.has_recent_playing_pattern(
            self.state.current_game.name,
            self.state.current_game.logs,
            playing_state.patterns,
            self.state.last_playing_timestamp,
        )

    # Recording completion helpers
    def _delete_recording(self, output_path: str) -> None:
        if os.path.exists(output_path):
            os.remove(output_path)
            logging.info(
                "[Detection] Deleted invalid play: '%s'", Path(output_path).name
            )
        else:
            logging.warning("[Detection] Recording file not found: %s", output_path)

    def _finalize_recording(self, output_path: str) -> None:
        lastplay = self.recording_manager.handle_recording_stopped(output_path)

        self.sound_service.play_ready()
        logging.info("[Detection] Saved as: '%s'", Path(lastplay).name)

    def _handle_scene_switching(self, state: str) -> None:
        """Handle automatic OBS scene switching based on game state."""
        if not self.state.current_game:
            return

        # Get the game shortname for scene configuration lookup
        game_shortname = self.state.current_game.shortname

        # Try to find a scene for this game and state
        scene_name = self.settings.get_scene_name(game_shortname, state)

        if scene_name:
            logging.info(
                "[Detection] Switching to scene '%s' for %s/%s",
                scene_name,
                game_shortname,
                state,
            )
            self.obs.set_current_scene(scene_name)
        else:
            # Add debug logging to help diagnose scene configuration issues
            logging.debug(
                "[Detection] No scene configured for %s/%s. Available scenes: %s",
                game_shortname,
                state,
                self.settings.scenes,
            )
            # Also log at info level for important states like Result
            if state in ["Result", "Select"]:
                logging.info(
                    "[Detection] No scene configured for %s/%s - check config.toml scenes section",
                    game_shortname,
                    state,
                )
