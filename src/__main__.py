"""
SIGMArec entry point.
"""

import ctypes
import logging
import os
import sys
import threading
import time

import keyboard

from __init__ import __version__
from config.settings import AppSettings, ConfigManager
from detection.engine import DetectionEngine
from games.repository import GameRepository
from obs.controller import OBSController


class SIGMArecApp:
    """Main application class that encapsulates all SIGMArec functionality."""

    def __init__(self):
        """Initialize the SIGMArec application."""
        self.settings: AppSettings = None
        self.obs: OBSController = None
        self.detection_engine: DetectionEngine = None
        self.repository: GameRepository = None
        self.hotkey_thread: threading.Thread = None
        self.hotkey_running: bool = False
        self.save_key_pressed: bool = False

    def setup_logging(self):
        """Configure logging for the application."""
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        log_file_path = os.path.join(script_dir, "SIGMArec.log")
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(log_file_path, mode="w", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        logging.info("Starting SIGMArec (%s)", __version__)

    def load_configuration(self):
        """Load application configuration."""
        logging.info("Loading config...")
        config = ConfigManager()
        self.settings = config.load_settings()

        logging.getLogger().setLevel(
            logging.DEBUG if self.settings.debug else logging.INFO
        )
        logging.getLogger("obsws_python").setLevel(
            logging.DEBUG if self.settings.debug else logging.WARNING
        )

    def load_games(self):
        """Load game configurations."""
        logging.info("Loading games...")
        self.repository = GameRepository()
        games = self.repository.load_all_games()
        logging.debug(self.repository.get_stats())
        return games

    def connect_obs(self):
        """Connect to OBS WebSocket."""
        logging.info("Connecting to OBS...")
        self.obs = OBSController.connect(self.settings)

    def initialize_detection_engine(self, games):
        """Initialize the detection engine."""
        self.detection_engine = DetectionEngine(self.obs, games, self.settings)
        self.obs.recording_completed_callback = (
            self.detection_engine.handle_recording_completed
        )

    def setup_hotkeys(self):
        """Setup keyboard hotkeys."""
        self.hotkey_running = True
        self.hotkey_thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self.hotkey_thread.start()

    def _hotkey_loop(self):
        """Hotkey monitoring loop."""
        while self.hotkey_running:
            key_pressed = keyboard.is_pressed(self.settings.save_key)
            if key_pressed and not self.save_key_pressed:
                self.save_lastplay()
            self.save_key_pressed = key_pressed
            time.sleep(0.05)

    def save_lastplay(self):
        """Save lastplay hotkey."""
        if not self.detection_engine:
            logging.warning("[Main] Detection engine not available")
            return

        if not self.detection_engine.can_save_lastplay():
            if not self.detection_engine.recording_manager.has_lastplay():
                logging.info("[Main] No lastplay available to save")
            else:
                current_state = self.detection_engine.state.current_state
                logging.info(
                    "[Main] Cannot save while playing (current state: %s)",
                    current_state,
                )

            self.detection_engine.sound_service.play_failed()
            return

        success, message = self.detection_engine.save_current_lastplay()

        if success:
            self.detection_engine.sound_service.play_saved()
            logging.info("[Main] Lastplay saved: %s", message)
        else:
            self.detection_engine.sound_service.play_failed()
            logging.error("[Main] Failed to save lastplay: %s", message)

    def main_loop(self):
        """Detection and recording loop."""
        if not self.detection_engine:
            return

        _ = self.detection_engine.detect_and_control()

    def run(self):
        """Application main loop."""
        try:
            logging.info("SIGMArec is running... Press Ctrl+C to exit at any time")
            while True:
                self.main_loop()
                time.sleep(self.settings.detection_interval)
        except KeyboardInterrupt:
            logging.info("SIGMArec is shutting down...")
        except ConnectionRefusedError:
            logging.error(
                "[OBS] Failed to connect: Retrying in %s seconds...",
                self.settings.obs_timeout,
            )
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources on shutdown."""
        self.hotkey_running = False
        if self.hotkey_thread and self.hotkey_thread.is_alive():
            self.hotkey_thread.join(timeout=1.0)

        keyboard.unhook_all()
        if self.obs:
            self.obs.shutdown()

    def initialize(self):
        """Initialize all application components."""
        self.setup_logging()
        self.load_configuration()
        games = self.load_games()
        self.connect_obs()
        self.initialize_detection_engine(games)
        self.setup_hotkeys()


def main():
    """Main entry point for the application."""
    ctypes.windll.kernel32.SetConsoleTitleW(f"SIGMArec ({__version__})")
    app = SIGMArecApp()
    app.initialize()
    app.run()


if __name__ == "__main__":
    main()
