"""
OBS WebSocket API wrapper.

Provides a simple interface for interacting with OBS.
"""

import logging
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, List, Optional

import obsws_python as obsws

from config.settings import AppSettings


@contextmanager
def _suppress_obsws_logging():
    """Context manager to temporarily suppress noisy obsws_python logging."""
    obsws_logger = logging.getLogger("obsws_python")
    websocket_logger = logging.getLogger("websocket")
    original_obsws_level = obsws_logger.level
    original_websocket_level = websocket_logger.level

    try:
        obsws_logger.setLevel(logging.CRITICAL)
        websocket_logger.setLevel(logging.CRITICAL)
        yield
    finally:
        obsws_logger.setLevel(original_obsws_level)
        websocket_logger.setLevel(original_websocket_level)


@dataclass
class OBSController:
    """OBS WebSocket API wrapper providing a simple interface for interacting with OBS."""

    config: AppSettings

    req_client: obsws.ReqClient
    event_client: obsws.EventClient

    _keep_alive_thread: Optional[threading.Thread] = None
    _keep_alive_stop_event: Optional[threading.Event] = None
    _connection_lost: bool = False

    _prev_recording_active: bool = False
    recording_active: bool = False

    recording_completed_callback: Optional[Callable[[str], None]] = None

    @property
    def is_connected(self) -> bool:
        """Check if we have active OBS clients and connection is not lost."""
        return (
            self.req_client is not None
            and self.event_client is not None
            and not self._connection_lost
        )

    @classmethod
    def connect(cls, settings: AppSettings) -> "OBSController":
        """Initialize the OBS WebSocket clients."""

        instance = cls(
            req_client=None,
            event_client=None,
            config=settings,
            recording_active=False,
            _connection_lost=False,
        )

        success = instance._attempt_connection()
        if success:
            logging.info("[OBS] Connected")
        else:
            logging.warning("[OBS] Failed to connect")

        instance._start_keep_alive_thread()

        return instance

    def _attempt_connection(self) -> bool:
        """Attempt to establish connection to OBS. Returns True if successful."""
        try:
            with _suppress_obsws_logging():
                req_client = obsws.ReqClient(
                    host=self.config.obs_host,
                    port=self.config.obs_port,
                    password=self.config.obs_password,
                    timeout=self.config.obs_timeout,
                )

                event_client = obsws.EventClient(
                    host=self.config.obs_host,
                    port=self.config.obs_port,
                    password=self.config.obs_password,
                    timeout=self.config.obs_timeout,
                )

                # Test the connection
                req_client.get_version()
                resp = req_client.get_record_status()

            self.req_client = req_client
            self.event_client = event_client
            self.recording_active = resp.output_active
            self._connection_lost = False

            self.register_events()

            return True

        except Exception as e:
            logging.debug("[OBS] Connection attempt failed: %s", str(e))
            self._connection_lost = True
            return False

    def _start_keep_alive_thread(self):
        """Start the background keep-alive monitoring thread."""
        if self._keep_alive_thread is not None:
            return

        self._keep_alive_stop_event = threading.Event()
        self._keep_alive_thread = threading.Thread(
            target=self._continuous_keep_alive,
            daemon=True,
            name="OBSController-KeepAlive",
        )
        self._keep_alive_thread.start()
        logging.debug("[OBS] Keep-alive thread started")

    def _continuous_keep_alive(self):
        """Continuously monitor connection and reconnect if needed."""
        while not self._keep_alive_stop_event.is_set():
            try:
                if not self.is_connected:
                    self._reconnect()
                else:
                    # Test connection with a simple API call
                    with _suppress_obsws_logging():
                        self.req_client.get_version()

                # Wait before next check
                self._keep_alive_stop_event.wait(self.config.obs_timeout)

            except Exception as e:
                logging.debug("[OBS] Keep-alive check failed: %s", str(e))
                self._connection_lost = True
                # Wait a bit before trying to reconnect
                self._keep_alive_stop_event.wait(1)

    def _reconnect(self):
        """Attempt to reconnect to OBS WebSocket."""
        logging.info("[OBS] Attempting to reconnect...")

        while not self._keep_alive_stop_event.is_set():
            if self._attempt_connection():
                logging.info("[OBS] Reconnected successfully")
                return
            self._keep_alive_stop_event.wait(1)

    def shutdown(self):
        """Gracefully shutdown the OBS controller and stop the keep-alive thread."""
        if self._keep_alive_stop_event is not None:
            self._keep_alive_stop_event.set()

        if self._keep_alive_thread is not None and self._keep_alive_thread.is_alive():
            self._keep_alive_thread.join(timeout=2.0)

        logging.debug("[OBS] Keep-alive thread stopped")

    def __del__(self):
        """Destructor to ensure cleanup when object is garbage collected."""
        self.shutdown()

    def register_events(self):
        """Register event callbacks."""
        if self.is_connected:
            try:
                self.event_client.callback.register(self.on_record_state_changed)
            except Exception as e:
                logging.debug("[OBS] Failed to register events: %s", str(e))
                self._connection_lost = True

    def on_record_state_changed(self, event):
        """Callback for when the recording state changes."""
        self._prev_recording_active = self.recording_active
        if event.output_state == "OBS_WEBSOCKET_OUTPUT_STARTED":
            self.recording_active = True
            logging.info("[OBS] Recording started")
        elif event.output_state == "OBS_WEBSOCKET_OUTPUT_STOPPED":
            self.recording_active = False
            logging.info("[OBS] Recording stopped ('%s')", event.output_path)

            if self.recording_completed_callback:
                self.recording_completed_callback(event.output_path)
            else:
                logging.debug("[OBS] Recording file available: %s", event.output_path)

    def start_recording(self):
        """Start recording."""
        if not self.recording_active and self.is_connected:
            try:
                with _suppress_obsws_logging():
                    self.req_client.start_record()
            except Exception as e:
                logging.debug("[OBS] Failed to start recording: %s", str(e))
                self._connection_lost = True

    def stop_recording(self):
        """Stop recording."""
        if self.recording_active and self.is_connected:
            try:
                self.req_client.stop_record()
            except Exception as e:
                logging.debug("[OBS] Failed to stop recording: %s", str(e))
                self._connection_lost = True

    def set_video_settings(
        self,
        base_width: int,
        base_height: int,
        output_width: int,
        output_height: int,
        fps: float = None,
    ):
        """
        Set OBS video settings (base canvas, output resolution, and optionally FPS).

        Args:
            base_width: Base canvas width
            base_height: Base canvas height
            output_width: Output scaled width
            output_height: Output scaled height
            fps: Frame rate (optional, preserves current if not specified)
        """
        if not self.is_connected:
            logging.debug("[OBS] Cannot set video settings - not connected")
            return

        try:
            with _suppress_obsws_logging():
                # Get current video settings first to preserve other settings
                current_settings = self.req_client.get_video_settings()

                # Determine FPS values to use
                if fps is not None:
                    # Convert fps to numerator/denominator (assuming denominator = 1 for simplicity)
                    fps_numerator = int(fps)
                    fps_denominator = 1
                else:
                    # Preserve current FPS
                    fps_numerator = current_settings.fps_numerator
                    fps_denominator = current_settings.fps_denominator

                # Update video settings
                self.req_client.set_video_settings(
                    base_width=base_width,
                    base_height=base_height,
                    out_width=output_width,
                    out_height=output_height,
                    numerator=fps_numerator,
                    denominator=fps_denominator,
                )

            if fps is not None:
                logging.info(
                    "[OBS][Video] Settings updated: Base %dx%d, Output %dx%d, FPS %s",
                    base_width,
                    base_height,
                    output_width,
                    output_height,
                    fps,
                )
            else:
                logging.info(
                    "[OBS][Video] Settings updated: Base %dx%d, Output %dx%d",
                    base_width,
                    base_height,
                    output_width,
                    output_height,
                )
        except Exception as e:
            logging.debug("[OBS] Failed to set video settings: %s", str(e))
            self._connection_lost = True

    def get_video_settings(self) -> Optional[dict]:
        """
        Get current OBS video settings.

        Returns:
            Dictionary containing video settings, or None if not connected or error occurred
        """
        if not self.is_connected:
            return None

        try:
            with _suppress_obsws_logging():
                response = self.req_client.get_video_settings()
            return {
                "base_width": response.base_width,
                "base_height": response.base_height,
                "output_width": response.output_width,
                "output_height": response.output_height,
                "fps_numerator": response.fps_numerator,
                "fps_denominator": response.fps_denominator,
            }
        except Exception as e:
            logging.debug("[OBS] Failed to get video settings: %s", str(e))
            self._connection_lost = True
            return None

    def set_current_scene(self, scene_name: str):
        """
        Switch to the specified scene.

        Args:
            scene_name: Name of the scene to switch to
        """
        if not self.is_connected:
            logging.debug(
                "[OBS] Cannot switch to scene '%s' - not connected", scene_name
            )
            return

        try:
            current_scene = self.get_current_scene()
            if current_scene != scene_name:
                with _suppress_obsws_logging():
                    self.req_client.set_current_program_scene(scene_name)
                logging.info("[OBS][Scene] '%s' → '%s'", current_scene, scene_name)
        except Exception as e:
            logging.debug(
                "[OBS] Failed to switch to scene '%s': %s", scene_name, str(e)
            )
            self._connection_lost = True

    def get_current_scene(self) -> Optional[str]:
        """
        Get the name of the currently active scene.

        Returns:
            Name of the current scene, or None if not connected or error occurred
        """
        if not self.is_connected:
            return None

        try:
            with _suppress_obsws_logging():
                response = self.req_client.get_current_program_scene()
            return response.current_program_scene_name
        except Exception as e:
            logging.debug("[OBS] Failed to get current scene: %s", str(e))
            self._connection_lost = True
            return None

    def get_scene_list(self) -> List[str]:
        """
        Get a list of all available scene names.

        Returns:
            List of scene names, or empty list if not connected or error occurred
        """
        if not self.is_connected:
            return []

        try:
            with _suppress_obsws_logging():
                response = self.req_client.get_scene_list()
            return [scene["sceneName"] for scene in response.scenes]
        except Exception as e:
            logging.debug("[OBS] Failed to get scene list: %s", str(e))
            self._connection_lost = True
            return []
