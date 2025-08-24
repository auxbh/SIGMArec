"""
SIGMArec entry point.
"""

import ctypes
import sys

from src import __version__
from core.application import Application


def main():
    """Main entry point for the application."""
    ctypes.windll.kernel32.SetConsoleTitleW(f"SIGMArec ({__version__})")

    app = Application()

    if app.initialize():
        app.run()
    else:
        print("Failed to initialize SIGMArec. Check logs for details.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
