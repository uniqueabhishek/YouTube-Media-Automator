"""Application directory and environment setup utilities.

This module provides functions to create and manage application directories,
including download folders and database paths.
"""


import os
import sys

APP_NAME = "My YT Downloads"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def get_base_path() -> str:
    """
    Returns the folder where the EXE/script resides.
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller executable
        # type: ignore[attr-defined]
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.dirname(os.path.abspath(__file__))


def get_app_folder() -> str:
    """
    Returns the main application folder path (created in the same location as EXE).
    """
    exe_dir = (
        os.path.dirname(os.path.abspath(sys.executable))
        if getattr(sys, "frozen", False)
        else os.getcwd()
    )
    app_folder = os.path.join(exe_dir, APP_NAME)
    os.makedirs(app_folder, exist_ok=True)
    return app_folder


def get_download_folder() -> str:
    """
    Returns default download folder path inside the app folder.
    """
    app_folder = get_app_folder()
    download_folder = os.path.join(app_folder, "Downloads")
    os.makedirs(download_folder, exist_ok=True)
    return download_folder


def get_database_path() -> str:
    """
    Returns path to SQLite database inside app folder.
    """
    app_folder = get_app_folder()
    db_path = os.path.join(app_folder, "downloads.db")
    return db_path
