"""
Screen capture service for pixel-based game detection.

This module captures only the focused window's client area for pattern matching.
"""

import logging
from typing import Optional

import mss
import win32gui
from mss.screenshot import ScreenShot


class ScreenCaptureService:
    """Service for capturing the focused window's client area for pixel-based detection."""

    def __init__(self):
        logging.debug("[ScreenCapture] Service initialized")

    def capture_focused_window(self) -> Optional[ScreenShot]:
        """
        Capture a screenshot of the focused window's client area (excluding window decorations).

        Returns:
            mss.ScreenShot: Screenshot object from mss with the focused window's content

        Raises:
            Exception: If no focused window found or capture fails
        """
        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            return None

        client_rect = win32gui.GetClientRect(hwnd)

        top_left = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
        bottom_right = win32gui.ClientToScreen(hwnd, (client_rect[2], client_rect[3]))

        monitor = {
            "left": top_left[0],
            "top": top_left[1],
            "width": bottom_right[0] - top_left[0],
            "height": bottom_right[1] - top_left[1],
        }

        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
        return screenshot

    def get_focused_window_title(self) -> str:
        """
        Get the title of the currently focused window.

        Returns:
            Window title or empty string if no window focused
        """
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return win32gui.GetWindowText(hwnd)
        return ""
