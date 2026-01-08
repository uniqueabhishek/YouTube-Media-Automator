#!/usr/bin/env python3
"""
YouTube Downloader - Hi Tech Version
Main Application Launcher

This is the primary entry point for the Hi Tech YouTube Downloader.
It provides a professional PyQt5 interface with advanced features including:
- Download queue management
- SQLite database for history tracking
- System tray integration
- Retry mechanism with error handling
- Format preview and selection
- Smart URL validation

Usage:
    python app.py

Author: Hi Tech Versions Team
"""

import sys
from PyQt5.QtWidgets import QApplication

# Import the main YouTubeDownloader class from the renamed module
from main_window import YouTubeDownloader


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # Create and show the main window
    window = YouTubeDownloader()
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    print("=" * 60)
    print("  YouTube Downloader - Hi Tech Version")
    print("=" * 60)
    print("Starting application...")
    print()

    main()
