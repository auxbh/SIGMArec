"""
Handles recording start/stop logic based on state transitions.
"""

import logging
import os
import threading
import time
from pathlib import Path

from audio import SoundService
from config.settings import AppSettings
from core.interfaces.detection import StateTransition
from core.interfaces.obs import IOBSController

from .scene_processor import SceneProcessor


class RecordingProcessor:
    """Processes state transitions to control recording operations."""

    def __init__(
        self,
        obs_controller: IOBSController,
        settings: AppSettings,
        scene_processor: SceneProcessor,
        sound_service: SoundService,
    ):
        """
        Initialize recording processor.

        Args:
            obs_controller: OBS controller for recording operations
            settings: Application settings
            scene_processor: Optional scene processor for checking recording delays
            sound_service: Sound service for playing sounds
        """
        self.obs = obs_controller
        self.settings = settings
        self.sound_service = sound_service
        self.scene_processor = scene_processor

        self._delete_next_recording = False
        self._restart_after_stop = False

    def process_transition(self, transition: StateTransition) -> None:
        """
        Process a state transition and control recording accordingly.

        Args:
            transition: State transition to process
        """
        patterns = set(transition.triggered_patterns)

        logging.debug(
            "[RecordingProcessor] [%s] %s → %s",
            transition.game.name,
            transition.from_state,
            transition.to_state,
        )

        if "restart" in patterns and self.obs.recording_active:
            logging.debug("[RecordingProcessor] Play restarted")
            self._delete_next_recording = True
            self._restart_after_stop = True
            self._stop_recording(immediate=True)
            return

        if "start_play" in patterns and not self.obs.recording_active:
            self._start_recording(play_sound=True)
            return

        if "discard_play" in patterns and self.obs.recording_active:
            self._delete_next_recording = True
            self._restart_after_stop = False
            self._stop_recording(immediate=True, sound="failed")
            return

        if "stop_play" in patterns and self.obs.recording_active:
            self._stop_recording(immediate=False)
            return

    def handle_recording_completed(self, output_path: str) -> bool:
        """
        Handle recording completion.

        Args:
            output_path: Path to completed recording

        Returns:
            True if the recording was deleted, False otherwise
        """
        should_delete = self._delete_next_recording
        self._delete_next_recording = False

        if self._restart_after_stop:
            logging.debug("[RecordingProcessor] Starting new recording after restart")
            self._restart_after_stop = False
            self._start_recording(play_sound=True)

        if should_delete:

            def _delete_recording():
                self._delete_recording(output_path)

            threading.Thread(target=_delete_recording, daemon=True).start()

        return should_delete

    def _start_recording(self, play_sound: bool = True) -> None:
        """
        Start recording with optional scene change delay.

        Args:
            play_sound: Whether to play start sound
        """
        if self.scene_processor:
            delay_remaining = self.scene_processor.get_recording_delay_remaining()
            if delay_remaining > 0:
                logging.debug(
                    "[RecordingProcessor] Delaying recording start by %.2fs",
                    delay_remaining,
                )

                def _delayed_start():
                    time.sleep(delay_remaining)
                    if not self.obs.recording_active:
                        self._start_recording_immediate(play_sound=play_sound)

                threading.Thread(target=_delayed_start, daemon=True).start()
                return

        self._start_recording_immediate(play_sound=play_sound)

    def _start_recording_immediate(self, play_sound: bool = True) -> None:
        """Start recording with optional sound feedback."""
        if play_sound:
            self.sound_service.play_start()
        self.obs.start_recording()

    def stop_recording_immediate(self, play_failed: bool = False) -> None:
        """Stop recording immediately with optional sound feedback."""
        if play_failed:
            self.sound_service.play_failed()
        self.obs.stop_recording()

    def mark_for_deletion(self) -> None:
        """Mark the next recording for deletion."""
        self._delete_next_recording = True

    def _stop_recording(self, immediate: bool, sound: str = None) -> None:
        """Stop recording with optional delay and sound feedback."""
        if not immediate:
            logging.debug(
                "[RecordingProcessor] Waiting %ss before stopping",
                self.settings.result_wait,
            )
            time.sleep(self.settings.result_wait)

        if sound:
            self.sound_service.play_sound(sound)

        self.obs.stop_recording()

    def _delete_recording(self, output_path: str) -> None:
        """Delete a recording file."""
        if os.path.exists(output_path):
            os.remove(output_path)
            logging.debug(
                "[RecordingProcessor] Deleted invalid play: '%s'",
                Path(output_path).name,
            )
        else:
            logging.warning(
                "[RecordingProcessor] Recording file not found: %s", output_path
            )
