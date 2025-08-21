"""
Process monitoring service for detecting running games.

This module handles process detection to identify which games are currently running.
"""

import logging
import time
from typing import List, Tuple

import psutil


class ProcessMonitor:
    """Service for monitoring running processes to detect active games."""

    def __init__(self, cache_duration: float = 1.0):
        self.cache_duration = cache_duration
        self._cached_processes: List[Tuple[str, str]] = []
        self._cache_time: float = 0.0

    def get_running_processes(self, use_cache: bool = True) -> List[Tuple[str, str]]:
        """
        Get a list of currently running processes.

        Args:
            use_cache: Whether to use cached results if available

        Returns:
            List of tuples (process_name, window_title)
        """
        current_time = time.time()

        if (
            use_cache
            and self._cached_processes
            and current_time - self._cache_time < self.cache_duration
        ):
            return self._cached_processes

        processes = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                process_name = proc.info["name"]

                window_title = self._get_window_title(proc)

                processes.append((process_name, window_title))

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        self._cached_processes = processes
        self._cache_time = current_time

        return processes

    def is_process_running(self, process_name: str, window_title: str = "") -> bool:
        """
        Check if a specific process is running.

        Args:
            process_name: Name of the process to check
            window_title: Optional window title to match

        Returns:
            True if process is running, False otherwise
        """
        running_processes = self.get_running_processes()

        for proc_name, proc_title in running_processes:
            if process_name.lower() in proc_name.lower():
                if window_title and window_title.lower() not in proc_title.lower():
                    continue
                return True

        return False

    def find_processes_by_pattern(self, pattern: str) -> List[Tuple[str, str]]:
        """
        Find all processes matching a pattern.

        Args:
            pattern: Pattern to match (supports wildcards with *)

        Returns:
            List of matching (process_name, window_title) tuples
        """
        running_processes = self.get_running_processes()
        matching_processes = []

        pattern_lower = pattern.lower().replace("*", "")

        for proc_name, proc_title in running_processes:
            if pattern_lower in proc_name.lower():
                matching_processes.append((proc_name, proc_title))

        return matching_processes

    def get_game_processes(
        self, game_process_patterns: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Get all running processes that match any of the given game patterns.

        Args:
            game_process_patterns: List of process name patterns to check

        Returns:
            List of matching (process_name, window_title) tuples
        """
        all_matches = []

        for pattern in game_process_patterns:
            matches = self.find_processes_by_pattern(pattern)
            all_matches.extend(matches)

        seen = set()
        unique_matches = []
        for proc in all_matches:
            if proc not in seen:
                seen.add(proc)
                unique_matches.append(proc)

        return unique_matches

    def clear_cache(self):
        """Clear the process cache to force fresh data on next request."""
        self._cached_processes = []
        self._cache_time = 0.0
        logging.debug("[ProcessMonitor] Cache cleared")

    def _get_window_title(self, process: psutil.Process) -> str:
        return process.info.get("name", "")
