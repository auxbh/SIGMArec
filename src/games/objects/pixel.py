"""
Pixel-based detection classes.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

from mss.screenshot import ScreenShot

from .base import Pattern, State


@dataclass
class Pixel:
    """A single pixel with position and expected RGB color with tolerance."""

    x: int
    y: int
    r: int
    g: int
    b: int
    tol: int

    def matches(self, screenshot: ScreenShot) -> bool:
        """
        Check if this pixel's color matches the color at its position in the screenshot.

        Args:
            screenshot: Screenshot object from mss with 'pixels' attribute and dimensions

        Returns:
            bool: True if the pixel color matches within tolerance, False otherwise
        """
        return self._is_within_bounds(screenshot) and self._color_matches(screenshot)

    @classmethod
    def from_config(cls, pixel_data: List[int]) -> "Pixel":
        """Create a Pixel from src.configuration data."""
        if len(pixel_data) < 6:
            raise ValueError(
                f"Pixel data must have at least 6 elements, got {len(pixel_data)}"
            )
        return cls(
            x=pixel_data[0],
            y=pixel_data[1],
            r=pixel_data[2],
            g=pixel_data[3],
            b=pixel_data[4],
            tol=pixel_data[5],
        )

    def _is_within_bounds(self, screenshot: ScreenShot) -> bool:
        """Check if pixel coordinates are within screenshot bounds."""
        return 0 <= self.x < screenshot.width and 0 <= self.y < screenshot.height

    def _color_matches(self, screenshot: ScreenShot) -> bool:
        """Check if pixel color matches within tolerance."""
        byte_index = (self.y * screenshot.width + self.x) * 4

        if byte_index + 3 >= len(screenshot.raw):
            logging.debug(
                "[Pixel] Byte index %d out of bounds for rawdata length: %d "
                "(x=%d, y=%d, screenshot=%dx%d)",
                byte_index,
                len(screenshot.raw),
                self.x,
                self.y,
                screenshot.width,
                screenshot.height,
            )
            return False

        screenshot_b = screenshot.raw[byte_index]
        screenshot_g = screenshot.raw[byte_index + 1]
        screenshot_r = screenshot.raw[byte_index + 2]

        return (
            abs(self.r - screenshot_r) <= self.tol
            and abs(self.g - screenshot_g) <= self.tol
            and abs(self.b - screenshot_b) <= self.tol
        )


@dataclass
class PixelPattern(Pattern):
    """A pattern for pixel-based detection using multiple pixel checks."""

    description: str
    resolution: List[int]
    pixels: List[Pixel]

    def matches(self, context: ScreenShot) -> bool:
        """
        Check if all pixels in this pattern match the context.

        Args:
            context: Screenshot object from mss

        Returns:
            bool: True if all pixels match, False otherwise
        """
        return self._resolution_matches(context) and self._all_pixels_match(context)

    def get_description(self) -> str:
        """Get a human-readable description of this pattern."""
        return f"Pixel pattern: {self.description} ({len(self.pixels)} pixels)"

    @classmethod
    def from_config(cls, config: Dict, **kwargs) -> "PixelPattern":
        """Create a PixelPattern from src.configuration data."""
        pixels = [
            Pixel.from_config(pixel_data) for pixel_data in config.get("pixels", [])
        ]
        return cls(
            description=config.get("description", ""),
            resolution=config.get("resolution", [1920, 1080]),
            pixels=pixels,
        )

    def _resolution_matches(self, context: ScreenShot) -> bool:
        """Check if screenshot resolution matches pattern resolution."""
        return (
            context.width == self.resolution[0] and context.height == self.resolution[1]
        )

    def _all_pixels_match(self, context: ScreenShot) -> bool:
        """Check if all pixels in the pattern match the screenshot."""
        return all(pixel.matches(context) for pixel in self.pixels)


@dataclass
class PixelState(State):
    """A game state detected through pixel patterns."""

    name: str
    patterns: List[PixelPattern]

    def matches(self, context: ScreenShot) -> bool:
        """
        Check if any of the patterns in this state match the screenshot.

        Args:
            context: Screenshot object from mss

        Returns:
            bool: True if any pattern matches, False otherwise
        """
        return any(pattern.matches(context) for pattern in self.patterns)

    def get_name(self) -> str:
        """Get the name of this state."""
        return self.name

    def get_pattern_descriptions(self) -> List[str]:
        """Get descriptions of all patterns in this state."""
        return [pattern.get_description() for pattern in self.patterns]

    @classmethod
    def from_config(cls, name: str, config: Dict) -> "PixelState":
        """Create a PixelState from src.configuration data."""
        patterns = [
            PixelPattern.from_config(pattern_config)
            for pattern_config in config.get("patterns", [])
        ]
        return cls(name=name, patterns=patterns)
