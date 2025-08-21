"""
Sound service for playing audio feedback during recording operations.

This module handles playing sound files using Windows built-in capabilities
to avoid adding extra dependencies.
"""

import logging
import os
import winsound
from pathlib import Path

from config import AppSettings


class SoundService:
    """Service for playing audio feedback sounds using Windows built-in capabilities."""

    def __init__(self, settings: AppSettings):
        """
        Initialize the sound service.

        Args:
            settings: Application settings containing sound file paths
        """
        self.settings = settings
        self._sound_paths = {}
        self._load_sound_paths()

        logging.debug("[SoundService] Sound service initialized")

    def _load_sound_paths(self):
        """Load and validate sound file paths."""
        sound_mappings = {
            "start": self.settings.start_sound,
            "ready": self.settings.ready_sound,
            "saved": self.settings.saved_sound,
            "failed": self.settings.failed_sound,
        }

        for sound_name, sound_path in sound_mappings.items():
            self._validate_sound_path(sound_name, sound_path)

    def _validate_sound_path(self, name: str, path: str):
        """
        Validate and store a sound file path.

        Args:
            name: Internal name for the sound
            path: Path to the sound file
        """
        if not os.path.isabs(path):
            if path.startswith("./"):
                relative_path = path[2:]

                dev_path = Path("assets") / relative_path
                packaged_path = Path(relative_path)

                if dev_path.exists():
                    full_path = dev_path
                elif packaged_path.exists():
                    full_path = packaged_path
                else:
                    full_path = packaged_path
            else:
                full_path = Path(path)
        else:
            full_path = Path(path)

        if full_path.exists():
            self._sound_paths[name] = str(full_path.resolve())
            logging.debug("[SoundService] Found sound %s", full_path)
        else:
            logging.warning("[SoundService] Sound file not found: %s", full_path)

    def play_sound(self, sound_name: str):
        """Play a sound by name."""
        if sound_name not in self._sound_paths:
            logging.debug("[SoundService] Sound %s not available", sound_name)
            return

        sound_path = self._sound_paths[sound_name]
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)

    def play_start(self):
        """Play recording start sound."""
        self.play_sound("start")

    def play_ready(self):
        """Play ready to save sound."""
        self.play_sound("ready")

    def play_saved(self):
        """Play save success sound."""
        self.play_sound("saved")

    def play_failed(self):
        """Play save failure sound."""
        self.play_sound("failed")

    def cleanup(self):
        """Clean up sound resources (no-op for this implementation)."""
        logging.debug("[SoundService] Sound service cleaned up")
