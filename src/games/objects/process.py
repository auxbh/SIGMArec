"""
Process-related classes for game detection.
"""

from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Information about a process to monitor for game detection."""

    exe: str
    title: str = ""

    def __post_init__(self):
        """Validate that at least one of exe or title is provided."""
        if not self.exe and not self.title:
            raise ValueError(
                "ProcessInfo must have at least one of 'exe' or 'title' specified"
            )

    def matches_process(self, process_name: str, window_title: str = "") -> bool:
        """Check if this ProcessInfo matches a running process."""
        if self.exe:
            if self.exe.startswith("*"):
                exe_match = process_name.endswith(self.exe[1:])
            else:
                exe_match = process_name == self.exe
        else:
            exe_match = True

        if self.title:
            title_match = self.title in window_title
        else:
            title_match = True

        return exe_match and title_match
