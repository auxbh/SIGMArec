"""
Dependency injection container for SIGMArec components.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

from src.audio import SoundService
from src.config import ConfigManager
from src.detection.engine import DetectionCoordinator
from src.detection.processors.recording_processor import RecordingProcessor
from src.detection.processors.scene_processor import SceneProcessor
from src.games import GameRepository


@dataclass
class Container:
    """
    Simple dependency injection container.

    Manages component lifecycle and dependencies for the application.
    """

    def __init__(self):
        """Initialize empty container."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}

    def register_singleton(self, service_type: str, instance: Any) -> None:
        """
        Register a singleton service instance.

        Args:
            service_type: Type name for the service
            instance: Service instance
        """
        self._singletons[service_type] = instance
        logging.debug("[Container] Registered singleton: %s", service_type)

    def get(self, service_type: str) -> Any:
        """
        Get a service instance.

        Args:
            service_type: Type name for the service

        Returns:
            Service instance

        Raises:
            KeyError: If service type not found
        """
        if service_type in self._singletons:
            return self._singletons[service_type]

        raise KeyError(f"Service not found: {service_type}")

    def has(self, service_type: str) -> bool:
        """
        Check if container has a service.

        Args:
            service_type: Type name to check

        Returns:
            True if service exists
        """
        return service_type in self._singletons

    def configure_application(self, config_path: str = "config.toml") -> "Container":
        """
        Configure the container with all application dependencies.

        Args:
            config_path: Path to configuration file

        Returns:
            Configured container instance
        """
        logging.debug("[Container] Configuring application dependencies")

        # Step 1: Load configuration
        config_manager = ConfigManager(config_path)
        settings = config_manager.load_settings()
        self.register_singleton("ConfigManager", config_manager)
        self.register_singleton("AppSettings", settings)

        # Step 2: Load games
        game_repository = GameRepository()
        games = game_repository.load_all_games()
        self.register_singleton("GameRepository", game_repository)
        self.register_singleton("Games", games)
        logging.debug("[Container] Loaded %d games", len(games))

        # Step 3: Initialize audio service
        sound_service = SoundService(settings)
        self.register_singleton("SoundService", sound_service)

        # Step 4: Initialize recording manager
        from src.obs import RecordingManager

        recording_manager = RecordingManager(settings, sound_service=sound_service)
        self.register_singleton("IRecordingManager", recording_manager)

        # Step 5: Initialize OBS controller
        from src.obs import OBSController

        obs_controller = OBSController.connect(settings)
        self.register_singleton("IOBSController", obs_controller)

        # Step 6: Initialize processors
        from src.detection.processors.video_processor import VideoProcessor

        video_processor = VideoProcessor(obs_controller, settings)
        self.register_singleton("VideoProcessor", video_processor)
        scene_processor = SceneProcessor(obs_controller, settings)
        self.register_singleton("SceneProcessor", scene_processor)
        recording_processor = RecordingProcessor(
            obs_controller, settings, scene_processor, sound_service
        )
        self.register_singleton("RecordingProcessor", recording_processor)

        # Step 7: Initialize detection engine
        detection_engine = DetectionCoordinator(
            obs_controller=obs_controller,
            recording_manager=recording_manager,
            games=games,
            settings=settings,
            video_processor=video_processor,
            scene_processor=scene_processor,
            recording_processor=recording_processor,
        )
        self.register_singleton("IDetectionEngine", detection_engine)

        logging.debug("[Container] Application dependencies configured")
        return self

    def cleanup(self) -> None:
        """Clean up all registered services."""
        logging.info("Cleaning up services")

        # Run cleanup or shutdown in reverse order from singleton registration
        for service_name in reversed(list(self._singletons.keys())):
            service = self._singletons[service_name]

            # Call cleanup method if it exists
            if hasattr(service, "cleanup"):
                try:
                    service.cleanup()
                    logging.debug("[Container] Cleaned up: %s", service_name)
                except Exception as e:
                    logging.error(
                        "[Container] Error cleaning up %s: %s", service_name, e
                    )
            # Otherwise, call shutdown method if it exists
            elif hasattr(service, "shutdown"):
                try:
                    service.shutdown()
                    logging.debug("[Container] Shut down: %s", service_name)
                except Exception as e:
                    logging.error(
                        "[Container] Error shutting down %s: %s", service_name, e
                    )

        self._singletons.clear()
        logging.debug("[Container] Cleanup complete")
