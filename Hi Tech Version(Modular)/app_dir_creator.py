# app_dir_creator.py

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

APP_NAME = "My YT Downloads"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def get_base_path() -> str:
    """
    Returns the folder where the EXE/script resides.
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller executable
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))  # type: ignore[attr-defined]
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


def get_ffmpeg_path() -> str:
    """
    Returns path to ffmpeg.exe if exists, otherwise empty string.
    """
    app_folder = get_app_folder()
    ffmpeg_path = os.path.join(app_folder, "bin", "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path

    # Check system-wide FFmpeg
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT)
        return "ffmpeg"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""  # Return empty string instead of None


def download_ffmpeg(destination: str | None = None) -> str:
    """
    Downloads and extracts FFmpeg to the app folder.
    Returns the path to ffmpeg.exe after download.
    """
    if destination is None:
        destination = os.path.join(get_app_folder(), "bin")
    os.makedirs(destination, exist_ok=True)

    zip_path = os.path.join(destination, "ffmpeg.zip")
    ffmpeg_exe_path = os.path.join(destination, "ffmpeg.exe")

    # Download FFmpeg zip
    try:
        print("Downloading FFmpeg...")
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
    except Exception as e:
        raise RuntimeError(f"Failed to download FFmpeg: {e}")

    # Extract ffmpeg.exe
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Search for ffmpeg.exe inside the zip
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe"):
                    zip_ref.extract(member, destination)
                    # Move ffmpeg.exe to root of bin folder
                    extracted_path = os.path.join(destination, member)
                    shutil.move(extracted_path, ffmpeg_exe_path)
                    # Remove leftover folders
                    leftover_dir = os.path.join(destination, member.split("/")[0])
                    if os.path.exists(leftover_dir):
                        shutil.rmtree(leftover_dir)
                    break
        os.remove(zip_path)
    except Exception as e:
        raise RuntimeError(f"Failed to extract FFmpeg: {e}")

    if not os.path.exists(ffmpeg_exe_path):
        raise RuntimeError("FFmpeg executable not found after extraction.")

    return ffmpeg_exe_path


def ensure_environment():
    """
    Ensures that all necessary folders exist and FFmpeg is available.
    """
    get_app_folder()
    get_download_folder()
    get_database_path()
    ffmpeg = get_ffmpeg_path()
    if not ffmpeg:
        print("FFmpeg not found. You can call download_ffmpeg() to install it.")
    return ffmpeg
