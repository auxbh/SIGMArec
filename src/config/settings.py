"""
Application configuration handling.
This module handles loading and managing application settings from config.toml.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import toml


class ConfigurationError(Exception):
    """Raised when there's an error with application configuration."""


class ValidationError(ConfigurationError):
    """Raised when configuration validation fails."""


class ConfigValidator:
    """Handles validation and type conversion of configuration values."""

    VALID_GAMES = {"IIDXINF", "SDVXEAC", "IIDX31", "IIDX32", "SDVXEG", "BMS"}
    VALID_STATES = {"Select", "Playing", "Result", "Default"}
    VALID_VIDEO_KEYS = {"Base", "Output", "FPS"}
    KEY_PATTERN = re.compile(
        r"^(?:(?:ctrl|alt|shift|cmd|win)\+)*"
        r'[a-zA-Z0-9_\-\+\[\]\\;\'",./`~!@#$%^&*()={}|:<>? ]$|'
        r"^(?:(?:ctrl|alt|shift|cmd|win)\+)*"
        r"(?:space|enter|escape|tab|backspace|delete|insert|home|end|"
        r"pageup|pagedown|up|down|left|right|f[1-9]|f1[0-2])$",
        re.IGNORECASE,
    )

    @staticmethod
    def validate_bool(value: Any, field_name: str, default: bool = False) -> bool:
        """Validate and convert boolean values."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_val = value.lower()
            if lower_val in ("true", "yes", "1", "on"):
                return True
            if lower_val in ("false", "no", "0", "off"):
                return False
            raise ValidationError(
                f"Invalid boolean value for {field_name}: '{value}'. Expected true/false."
            )
        raise ValidationError(
            f"Invalid type for {field_name}: expected boolean, got {type(value).__name__}"
        )

    @staticmethod
    def validate_int(
        value: Any,
        field_name: str,
        default: int = 0,
        min_val: int = None,
        max_val: int = None,
    ) -> int:
        """Validate and convert integer values with optional bounds checking."""
        if value is None:
            return default

        try:
            if isinstance(value, str):
                int_val = int(value)
            elif isinstance(value, (int, float)):
                int_val = int(value)
            else:
                raise ValidationError(
                    f"Invalid type for {field_name}: expected int, got {type(value).__name__}"
                )

            if min_val is not None and int_val < min_val:
                raise ValidationError(
                    f"Value for {field_name} ({int_val}) is below minimum ({min_val})"
                )
            if max_val is not None and int_val > max_val:
                raise ValidationError(
                    f"Value for {field_name} ({int_val}) is above maximum ({max_val})"
                )

            return int_val
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid integer value for {field_name}: '{value}' - {e}"
            ) from e

    @staticmethod
    def validate_float(
        value: Any,
        field_name: str,
        default: float = 0.0,
        min_val: float = None,
        max_val: float = None,
    ) -> float:
        """Validate and convert float values with optional bounds checking."""
        if value is None:
            return default

        try:
            if isinstance(value, str):
                float_val = float(value)
            elif isinstance(value, (int, float)):
                float_val = float(value)
            else:
                raise ValidationError(
                    f"Invalid type for {field_name}: expected float, got {type(value).__name__}"
                )

            if min_val is not None and float_val < min_val:
                raise ValidationError(
                    f"Value for {field_name} ({float_val}) is below minimum ({min_val})"
                )
            if max_val is not None and float_val > max_val:
                raise ValidationError(
                    f"Value for {field_name} ({float_val}) is above maximum ({max_val})"
                )

            return float_val
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid float value for {field_name}: '{value}' - {e}"
            ) from e

    @staticmethod
    def validate_string(
        value: Any, field_name: str, default: str = "", allow_empty: bool = True
    ) -> str:
        """Validate and convert string values."""
        if value is None:
            return default

        if not isinstance(value, str):
            # Convert to string if possible
            try:
                str_val = str(value)
            except Exception as e:
                raise ValidationError(
                    f"Cannot convert {field_name} to string: {e}"
                ) from e
        else:
            str_val = value

        if not allow_empty and not str_val.strip():
            raise ValidationError(f"{field_name} cannot be empty")

        return str_val

    @staticmethod
    def validate_keyboard_key(
        value: Any, field_name: str, default: str = "space"
    ) -> str:
        """Validate keyboard key combinations."""
        key_str = ConfigValidator.validate_string(
            value, field_name, default, allow_empty=False
        )

        if not ConfigValidator.KEY_PATTERN.match(key_str):
            raise ValidationError(
                f"Invalid keyboard key format for {field_name}: '{key_str}'. "
                f"Expected: 'key' or 'modifier+key' (e.g. 'space', 'ctrl+s', 'ctrl+shift+space')"
            )

        return key_str.lower()

    @staticmethod
    def validate_file_path(
        value: Any, field_name: str, default: str = "", check_exists: bool = False
    ) -> str:
        """Validate file paths with optional existence checking."""
        path_str = ConfigValidator.validate_string(
            value, field_name, default, allow_empty=False
        )

        if check_exists:
            path_obj = Path(path_str)
            if not path_obj.exists():
                raise ValidationError(
                    f"File does not exist for {field_name}: '{path_str}'"
                )

        return path_str

    @staticmethod
    def validate_scenes(value: Any, field_name: str) -> Dict[str, Dict[str, str]]:
        """Validate scene configuration structure with support for default values."""
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a dictionary")

        validated_scenes = {}

        for key, config in value.items():
            if key in ConfigValidator.VALID_GAMES:
                # Game-specific scene configuration
                game = key
                states = config

                # Validate states structure
                if not isinstance(states, dict):
                    raise ValidationError(
                        f"Scene config for '{game}' must be a dictionary of state->scene mappings"
                    )

                validated_states = {}
                for state, scene_name in states.items():
                    # Validate state name
                    if state not in ConfigValidator.VALID_STATES:
                        raise ValidationError(
                            f"Invalid state '{state}' for game '{game}' in {field_name}. "
                            f"Valid states: {', '.join(sorted(ConfigValidator.VALID_STATES))}"
                        )

                    # Validate scene name
                    scene_str = ConfigValidator.validate_string(
                        scene_name, f"{field_name}.{game}.{state}", allow_empty=False
                    )
                    validated_states[state] = scene_str

                validated_scenes[game] = validated_states

            elif key in ConfigValidator.VALID_STATES:
                # Default scene configuration
                if "Default" not in validated_scenes:
                    validated_scenes["Default"] = {}

                # Validate scene name
                scene_str = ConfigValidator.validate_string(
                    config, f"{field_name}.{key}", allow_empty=False
                )
                validated_scenes["Default"][key] = scene_str

            else:
                raise ValidationError(
                    f"Invalid key '{key}' in {field_name}. "
                    f"Valid games: {', '.join(sorted(ConfigValidator.VALID_GAMES))} "
                    f"Valid states: {', '.join(sorted(ConfigValidator.VALID_STATES))}"
                )

        return validated_scenes

    @staticmethod
    def validate_video(value: Any, field_name: str) -> Dict[str, Dict[str, str]]:
        """Validate video settings configuration structure with support for default values."""
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a dictionary")

        validated_video = {}

        for key, config in value.items():
            if key in ConfigValidator.VALID_GAMES:
                # Game-specific video configuration
                game = key
                video_config = config

                # Validate video configuration structure
                if not isinstance(video_config, dict):
                    raise ValidationError(
                        f"Video configuration for '{game}' must be a dictionary"
                    )

                # Validate video settings
                validated_config = {}
                for setting_type, setting_value in video_config.items():
                    validated_setting = ConfigValidator._validate_video_setting(
                        setting_type, setting_value, f"{field_name}.{game}"
                    )
                    validated_config[setting_type] = validated_setting

                validated_video[game] = validated_config

            elif key in ConfigValidator.VALID_VIDEO_KEYS:
                # Default video configuration
                if "Default" not in validated_video:
                    validated_video["Default"] = {}

                # Validate video setting
                validated_setting = ConfigValidator._validate_video_setting(
                    key, config, field_name
                )
                validated_video["Default"][key] = validated_setting

            else:
                raise ValidationError(
                    f"Invalid key '{key}' in {field_name}. "
                    f"Valid games: {', '.join(sorted(ConfigValidator.VALID_GAMES))} "
                    f"Valid video settings: {', '.join(sorted(ConfigValidator.VALID_VIDEO_KEYS))}"
                )

        return validated_video

    @staticmethod
    def _validate_video_setting(
        setting_type: str, setting_value: Any, field_prefix: str
    ) -> str:
        """Helper method to validate individual video settings."""
        # Validate setting type
        if setting_type not in ConfigValidator.VALID_VIDEO_KEYS:
            raise ValidationError(
                f"Invalid video setting '{setting_type}' in {field_prefix}. "
                f"Valid settings: {', '.join(sorted(ConfigValidator.VALID_VIDEO_KEYS))}"
            )

        if setting_type == "FPS":
            try:
                fps_value = float(setting_value)
                if fps_value <= 0:
                    raise ValueError("FPS must be positive")
                if fps_value > 240:
                    raise ValueError("FPS exceeds maximum supported (240)")

                return str(fps_value)
            except (ValueError, TypeError) as e:
                raise ValidationError(
                    f"Invalid FPS '{setting_value}' for {field_prefix}.{setting_type}."
                    f" Expected a positive number (e.g. '60', '30', '120'). Error: {e}"
                ) from e
        else:
            resstr = ConfigValidator.validate_string(
                setting_value,
                f"{field_prefix}.{setting_type}",
                allow_empty=False,
            )

            try:
                parts = resstr.split("x")
                if len(parts) != 2:
                    raise ValueError("Resolution must have exactly 2 values")

                width = int(parts[0].strip())
                height = int(parts[1].strip())

                if width <= 0 or height <= 0:
                    raise ValueError("Width and height must be positive integers")

                if width > 3840 or height > 2160:
                    raise ValueError("Resolution exceeds maximum supported (3840x2160)")

                return f"{width}x{height}"

            except (ValueError, IndexError) as e:
                raise ValidationError(
                    f"Invalid resolution '{resstr}' for {field_prefix}.{setting_type}."
                    f" Expected: 'widthxheight' (e.g. '1920x1080')."
                ) from e


@dataclass
class AppSettings:
    """Application settings data class matching config.toml structure."""

    save_key: str = "space"
    debug: bool = False

    obs_host: str = "localhost"
    obs_port: int = 4455
    obs_password: str = ""
    obs_timeout: int = 3

    start_sound: str = "./sounds/start.wav"
    ready_sound: str = "./sounds/ready.wav"
    saved_sound: str = "./sounds/saved.wav"
    failed_sound: str = "./sounds/failed.wav"

    detection_interval: float = 0.25
    detections_required: int = 2

    result_wait: float = 2
    organize_by_game: bool = True
    save_thumbnails: bool = True

    scenes: Dict[str, Dict[str, str]] = None
    video: Dict[str, Dict[str, str]] = None

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.scenes is None:
            self.scenes = {}
        if self.video is None:
            self.video = {}

    def get_scene_name(self, game: str, state: str) -> Optional[str]:
        """
        Get scene name for a specific game and state with fallback to defaults.

        Args:
            game: Game shortname (e.g., 'IIDX31', 'BMS')
            state: Game state (e.g., 'Playing', 'Result', 'Select', 'Default')

        Returns:
            Scene name if found, None if no configuration exists
        """
        # First check game-specific configuration
        if game in self.scenes and state in self.scenes[game]:
            return self.scenes[game][state]

        # Fall back to default configuration for state if it exists
        if state in self.scenes["Default"]:
            return self.scenes["Default"][state]

        # Fall back to default scene if it exists
        if "Default" in self.scenes:
            return self.scenes["Default"]["Default"]

        return None

    def get_video_setting(self, game: str, setting: str) -> Optional[str]:
        """
        Get video setting for a specific game with fallback to defaults.

        Args:
            game: Game shortname (e.g., 'IIDX31', 'BMS')
            setting: Video setting type ('Base', 'Output', 'FPS')

        Returns:
            Setting value if found, None if no configuration exists
        """
        # First check game-specific configuration
        if game in self.video and setting in self.video[game]:
            return self.video[game][setting]

        # Fall back to default video configuration if it exists
        if "Default" in self.video and setting in self.video["Default"]:
            return self.video["Default"][setting]

        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary matching config.toml structure."""
        result = {
            "input": {
                "save_key": self.save_key,
                "debug": self.debug,
            },
            "obs": {
                "host": self.obs_host,
                "port": self.obs_port,
                "password": self.obs_password,
                "timeout": self.obs_timeout,
            },
            "audio": {
                "start": self.start_sound,
                "ready": self.ready_sound,
                "saved": self.saved_sound,
                "failed": self.failed_sound,
            },
            "detection": {
                "interval": self.detection_interval,
                "detections_required": self.detections_required,
            },
            "recording": {
                "result_wait": self.result_wait,
                "organize_by_game": self.organize_by_game,
                "save_thumbnails": self.save_thumbnails,
            },
        }

        if self.scenes:
            result["scenes"] = self.scenes

        if self.video:
            result["video"] = self.video

        return result


class ConfigManager:
    """Manages application configuration loading and saving."""

    def __init__(self, config_path: str = "config.toml"):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self._settings: Optional[AppSettings] = None

    def load_settings(self) -> AppSettings:
        """
        Load application settings from config file.

        Returns:
            AppSettings object with loaded or default settings
        """
        if self._settings is not None:
            return self._settings

        if not self.config_path.exists():
            self._settings = AppSettings()
            self.save_settings(self._settings)
            return self._settings

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = toml.load(f)

            self._settings = self._parse_config_data(config_data)
            return self._settings

        except Exception as e:
            raise ConfigurationError(
                f"Error loading configuration from {self.config_path}: {e}"
            ) from e

    def save_settings(self, settings: AppSettings) -> None:
        """
        Save application settings to config file.

        Args:
            settings: AppSettings object to save
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                toml.dump(settings.to_dict(), f)

            self._settings = settings

        except Exception as e:
            raise ConfigurationError(
                f"Error saving configuration to {self.config_path}: {e}"
            ) from e

    def get_setting(self, key: str, default=None):
        """Get a specific setting value."""
        settings = self.load_settings()
        return getattr(settings, key, default)

    def update_setting(self, key: str, value: Any) -> None:
        """Update a specific setting and save."""
        settings = self.load_settings()
        if hasattr(settings, key):
            setattr(settings, key, value)
            self.save_settings(settings)
        else:
            raise ValueError(f"Unknown setting: {key}")

    def _parse_config_data(self, config_data: Dict[str, Any]) -> AppSettings:
        """Parse and validate configuration data into AppSettings object."""

        # Extract sections with defaults for missing sections
        input_config = config_data.get("input", {})
        obs_config = config_data.get("obs", {})
        audio_config = config_data.get("audio", {})
        detection_config = config_data.get("detection", {})
        recording_config = config_data.get("recording", {})

        # Handle scenes configuration
        scenes = {}
        scenes_config = config_data.get("scenes", {})
        if isinstance(scenes_config, dict):
            scenes = scenes_config.copy()

        # Also handle [scenes.GAME] format
        for key, value in config_data.items():
            if key.startswith("scenes.") and isinstance(value, dict):
                game_shortname = key[7:]  # Remove 'scenes.' prefix
                scenes[game_shortname] = value

        # Handle video configuration
        video = {}
        video_config = config_data.get("video", {})
        if isinstance(video_config, dict):
            video = video_config.copy()

        # Also handle [video.GAME] format
        for key, value in config_data.items():
            if key.startswith("video.") and isinstance(value, dict):
                game_shortname = key[6:]  # Remove 'video.' prefix
                video[game_shortname] = value

        try:
            return AppSettings(
                # Input section validation
                save_key=ConfigValidator.validate_keyboard_key(
                    input_config.get("save_key"), "input.save_key", "ctrl+space"
                ),
                debug=ConfigValidator.validate_bool(
                    input_config.get("debug"), "input.debug", False
                ),
                # OBS section validation
                obs_host=ConfigValidator.validate_string(
                    obs_config.get("host"), "obs.host", "localhost", allow_empty=False
                ),
                obs_port=ConfigValidator.validate_int(
                    obs_config.get("port"), "obs.port", 4455, min_val=1, max_val=65535
                ),
                obs_password=ConfigValidator.validate_string(
                    obs_config.get("password"), "obs.password", ""
                ),
                obs_timeout=ConfigValidator.validate_int(
                    obs_config.get("timeout"), "obs.timeout", 3, min_val=1, max_val=300
                ),
                # Audio section validation
                start_sound=ConfigValidator.validate_file_path(
                    audio_config.get("start"), "audio.start", "./sounds/start.wav"
                ),
                ready_sound=ConfigValidator.validate_file_path(
                    audio_config.get("ready"), "audio.ready", "./sounds/ready.wav"
                ),
                saved_sound=ConfigValidator.validate_file_path(
                    audio_config.get("saved"), "audio.saved", "./sounds/saved.wav"
                ),
                failed_sound=ConfigValidator.validate_file_path(
                    audio_config.get("failed"), "audio.failed", "./sounds/failed.wav"
                ),
                # Detection section validation
                detection_interval=ConfigValidator.validate_float(
                    detection_config.get("interval"),
                    "detection.interval",
                    0.25,
                    min_val=0.01,
                    max_val=10.0,
                ),
                detections_required=ConfigValidator.validate_int(
                    detection_config.get("detections_required"),
                    "detection.detections_required",
                    2,
                    min_val=1,
                    max_val=20,
                ),
                # Recording section validation
                result_wait=ConfigValidator.validate_float(
                    recording_config.get("result_wait"),
                    "recording.result_wait",
                    2.0,
                    min_val=0.0,
                    max_val=120.0,
                ),
                organize_by_game=ConfigValidator.validate_bool(
                    recording_config.get("organize_by_game"),
                    "recording.organize_by_game",
                    True,
                ),
                save_thumbnails=ConfigValidator.validate_bool(
                    recording_config.get("save_thumbnails"),
                    "recording.save_thumbnails",
                    True,
                ),
                # Scene configuration validation
                scenes=ConfigValidator.validate_scenes(scenes, "scenes"),
                # Video settings configuration validation
                video=ConfigValidator.validate_video(video, "video"),
            )

        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}") from e
        except Exception as e:
            raise ConfigurationError(
                f"Unexpected error during configuration parsing: {e}"
            ) from e
