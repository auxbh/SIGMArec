"""
Log-based detection classes.
"""

from dataclasses import dataclass
from typing import Dict, List

from .base import Pattern, State


@dataclass
class LogPattern(Pattern):
    """A pattern for log-based detection using class and method names."""

    class_name: str
    method_name: str
    description: str = ""

    def matches(self, context: List[Dict]) -> bool:
        """
        Check if this pattern matches any of the recent log entries.
        Returns True if the class and method are found in any log entry.

        Args:
            log_entries: List of dictionaries with 'class' and 'method' keys
        """
        for entry in context:
            entry_class = entry.get("class", "")
            entry_method = entry.get("method", "")

            if self.class_name in entry_class and self.method_name in entry_method:
                return True
        return False

    def get_description(self) -> str:
        """Get a human-readable description of this pattern."""
        return self.description or f"Log pattern: {self.class_name}.{self.method_name}"

    @classmethod
    def from_config(cls, config: Dict, **kwargs) -> "LogPattern":
        """Create a LogPattern from configuration data."""
        return cls(
            class_name=config.get("class", ""),
            method_name=config.get("method", ""),
            description=config.get("description", ""),
        )


@dataclass
class LogState(State):
    """A game state detected through log patterns."""

    name: str
    patterns: List[LogPattern]

    def matches(self, context: List[Dict]) -> bool:
        """Check if any of the patterns in this state match the log entries."""
        return any(pattern.matches(context) for pattern in self.patterns)

    def get_last_match_position(self, log_entries: List[Dict]) -> int:
        """
        Get the position of the last matching pattern in the log entries.

        Args:
            log_entries: List of log entry dictionaries in chronological order

        Returns:
            Index of the last matching entry, or -1 if no matches found
        """
        last_match_pos = -1

        for i, entry in enumerate(log_entries):
            if any(pattern.matches([entry]) for pattern in self.patterns):
                last_match_pos = i

        return last_match_pos

    def get_last_match_timestamp(self, log_entries: List[Dict]) -> str:
        """
        Get the timestamp of the last matching pattern in the log entries.

        Args:
            log_entries: List of log entry dictionaries in chronological order

        Returns:
            Timestamp string of the last matching entry, or empty string if no matches found
        """
        last_match_pos = self.get_last_match_position(log_entries)
        if last_match_pos >= 0:
            return log_entries[last_match_pos].get("date", "")
        return ""

    def get_name(self) -> str:
        """Get the name of this state."""
        return self.name

    def get_pattern_descriptions(self) -> List[str]:
        """Get descriptions of all patterns in this state."""
        return [pattern.get_description() for pattern in self.patterns]

    @classmethod
    def from_config(cls, name: str, config: Dict) -> "LogState":
        """Create a LogState from configuration data."""
        patterns = [
            LogPattern.from_config(pattern_config)
            for pattern_config in config.get("patterns", [])
        ]
        return cls(name=name, patterns=patterns)
