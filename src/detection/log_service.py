"""
Log service for detecting Java-based games and reading their log files.

This module handles finding Java processes, extracting JAR paths, and reading log files
for log-based game state detection.
"""

import ctypes
import logging
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

import psutil
import wmi


class LogService:
    """Service for Java process detection and log file reading."""

    def __init__(self):
        self.user32 = ctypes.windll.user32
        self._wmi_conn = None
        self._log_cache: Dict[str, List[Dict[str, str]]] = {}

    def get_foreground_java_process_info(self) -> Optional[Tuple[int, str]]:
        """
        Get information about the foreground Java process.

        Returns:
            Tuple of (pid, jar_path) if foreground process is Java, None otherwise
        """
        hwnd = self.user32.GetForegroundWindow()
        if not hwnd:
            return None

        pid = ctypes.c_ulong()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        pid_value = pid.value

        try:
            process = psutil.Process(pid_value)
            if process.name().lower() != "java.exe":
                return None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

        jar_path = self._get_jar_path_from_java_process(pid_value)
        if jar_path:
            return (pid_value, jar_path)
        return None

    def find_log_file(self, jar_path: str, log_filename: str) -> Optional[str]:
        """
        Find a log file in the same directory as the JAR file.

        Args:
            jar_path: Path to the JAR file
            log_filename: Name of the log file to find

        Returns:
            Absolute path to the log file or None if not found
        """
        jar_dir = os.path.dirname(jar_path)
        log_path = os.path.join(jar_dir, log_filename)

        if os.path.exists(log_path):
            return os.path.abspath(log_path)
        return None

    def read_log_entries(
        self, log_path: str, max_entries: int = 100
    ) -> List[Dict[str, str]]:
        """
        Read recent log entries from an XML log file.

        Args:
            log_path: Path to the XML log file
            max_entries: Maximum number of recent entries to return

        Returns:
            List of dictionaries with 'class', 'method', 'message' keys from recent log entries
        """
        try:
            if not os.path.exists(log_path):
                return []

            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (PermissionError, OSError) as e:
                logging.debug("[LogService] File access error for %s: %s", log_path, e)
                return []

            content = self._clean_xml_content(content)

            if not content.strip():
                logging.debug("[LogService] Empty log file: %s", log_path)
                return []

            records = ET.fromstring(content).findall(".//record")

            entries = []
            for record in (
                records[-max_entries:] if len(records) > max_entries else records
            ):
                entry = {
                    "class": (
                        record.find("class").text.strip()
                        if record.find("class") is not None
                        and record.find("class").text
                        else ""
                    ),
                    "method": (
                        record.find("method").text.strip()
                        if record.find("method") is not None
                        and record.find("method").text
                        else ""
                    ),
                    "message": (
                        record.find("message").text.strip()
                        if record.find("message") is not None
                        and record.find("message").text
                        else ""
                    ),
                    "date": (
                        record.find("date").text.strip()
                        if record.find("date") is not None and record.find("date").text
                        else ""
                    ),
                }

                if entry["class"] and entry["method"]:
                    entries.append(entry)

            return entries

        except ET.ParseError as e:
            logging.debug(
                "[LogService] XML error in %s: %s (file may be incomplete/actively being written)",
                log_path,
                e,
            )
            return []

    def get_log_entries_for_game(
        self, game_name: str, log_filename: str
    ) -> List[Dict[str, str]]:
        """
        Get log entries for a specific game if it's currently focused.

        Args:
            game_name: Name of the game for logging purposes
            log_filename: Name of the log file to look for

        Returns:
            List of structured log entry dictionaries or empty list if not found
        """
        java_info = self.get_foreground_java_process_info()
        if not java_info:
            return []

        _, jar_path = java_info

        log_path = self.find_log_file(jar_path, log_filename)
        if not log_path:
            logging.debug(
                "[LogService] Log file '%s' not found for %s",
                log_filename,
                game_name,
            )
            return []

        entries = self.read_log_entries(log_path)

        return entries

    def get_recent_log_messages(
        self, log_path: str, since_last_check: bool = True
    ) -> List[Dict[str, str]]:
        """
        Get recent log messages, optionally only since the last check.

        Args:
            log_path: Path to the log file
            since_last_check: If True, only return messages since last check

        Returns:
            List of recent structured log entry dictionaries
        """
        all_messages = self.read_log_entries(log_path)

        if not since_last_check:
            return all_messages

        cache_key = log_path
        if cache_key in self._log_cache:
            last_entries = self._log_cache[cache_key]

            if len(all_messages) > len(last_entries):
                new_entries = all_messages[len(last_entries) :]
                self._log_cache[cache_key] = all_messages
                return new_entries
            else:
                return []
        else:
            self._log_cache[cache_key] = all_messages
            return all_messages[-10:]

    def has_recent_playing_pattern(
        self,
        game_name: str,
        log_filename: str,
        playing_patterns: List,
        since_timestamp: Optional[str] = None,
    ) -> bool:
        """
        Check if there are recent playing pattern matches in the log file.

        This method checks for playing patterns that occurred after a given timestamp,
        which can be used to detect new playing sessions even when already in playing state.

        Args:
            game_name: Name of the game for logging purposes
            log_filename: Name of the log file to look for
            playing_patterns: List of LogPattern objects for the Playing state
            since_timestamp: Timestamp to check from. If None, checks last 10 entries

        Returns:
            True if there are recent playing patterns, False otherwise
        """
        java_info = self.get_foreground_java_process_info()
        if not java_info:
            return False

        _, jar_path = java_info
        log_path = self.find_log_file(jar_path, log_filename)
        if not log_path:
            return False

        # Get recent entries
        if since_timestamp:
            all_entries = self.read_log_entries(log_path)
            # Find entries after the given timestamp
            recent_entries = []
            for entry in reversed(all_entries):  # Start from newest
                if entry.get("date", "") > since_timestamp:
                    recent_entries.insert(
                        0, entry
                    )  # Insert at beginning to maintain order
                else:
                    break
        else:
            # Just check the last few entries
            recent_entries = self.read_log_entries(log_path, max_entries=10)

        if not recent_entries:
            return False

        # Check if any playing patterns match the recent entries
        for pattern in playing_patterns:
            if pattern.matches(recent_entries):
                logging.debug(
                    "[LogService] Found recent playing pattern for %s: %s.%s",
                    game_name,
                    pattern.class_name,
                    pattern.method_name,
                )
                return True

        return False

    def _clean_xml_content(self, content: str) -> str:
        """
        Clean XML content to handle common issues like empty lines and incomplete records.

        Args:
            content: Raw XML content from the log file

        Returns:
            Cleaned XML content that can be safely parsed
        """
        lines = content.splitlines()
        cleaned_lines = []
        in_record = False
        record_depth = 0

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if "<record>" in stripped:
                in_record = True
                record_depth += stripped.count("<record>") - stripped.count("</record>")
            elif "</record>" in stripped:
                record_depth -= stripped.count("</record>") - stripped.count("<record>")
                if record_depth <= 0:
                    in_record = False
                    record_depth = 0

            if (
                stripped.startswith("<?xml")
                or stripped.startswith("<!DOCTYPE")
                or stripped.startswith("<log>")
                or stripped.startswith("</log>")
                or (in_record and record_depth > 0)
                or stripped == "</record>"
            ):
                cleaned_lines.append(line)

        cleaned_content = "\n".join(cleaned_lines)

        if "</log>" not in cleaned_content and "<log>" in cleaned_content:
            cleaned_content += "\n</log>"

        return cleaned_content

    def _get_jar_path_from_java_process(self, pid: int) -> Optional[str]:
        if not self._wmi_conn:
            self._wmi_conn = wmi.WMI()

        processes = self._wmi_conn.Win32_Process(ProcessId=pid)
        if not processes:
            return None

        cmdline = processes[0].CommandLine
        if not cmdline or "-cp" not in cmdline:
            return None

        cwd = psutil.Process(pid).cwd()

        cp_part = cmdline.split("-cp", 1)[1].strip()
        cp_entries = cp_part.split(" ", 1)[0]

        for entry in cp_entries.split(";"):
            if entry.lower().endswith(".jar"):
                if not os.path.isabs(entry):
                    entry = os.path.join(cwd, entry)
                return os.path.abspath(entry)
        return None
