"""YouTube Downloader main window module.

This module contains the YouTubeDownloader class which provides the main
GUI interface for downloading YouTube videos using PyQt5.
"""
import os
import re
import sys

import yt_dlp
from loguru import logger

# pylint: disable=no-name-in-module
from PyQt5.QtCore import QSettings, Qt, QTimer  # type: ignore

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import (  # type: ignore
    QAction,
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from app_dir_creator import get_database_path, get_download_folder
from database_handler import DatabaseManager, init_db
from download_thread import DownloadThread
from ffmpeg_utils import get_ffmpeg_path as find_ffmpeg
from queue_item import QueueItem, QueueStatus
from smart_paste_utils import UrlLineEdit
from title_fetch_thread import TitleFetchThread

logger.add("downloader.log", rotation="500 KB")


# class UrlLineEdit(QLineEdit, SmartPasteMixin):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


# ======================= Helper Functions =======================
def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and remove dangerous characters.
    Removes: < > : " / \\ | ? * and control characters (0x00-0x1F)
    """
    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "video"
    return sanitized


def validate_url(url: str) -> bool:
    """
    Validate if the URL is a valid YouTube URL.
    Returns True if valid, False otherwise.
    """
    # Basic URL pattern for YouTube
    youtube_pattern = (
        r"^https?://(www\.)?"
        r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|v/)|youtu\.be/).+"
    )
    return bool(re.match(youtube_pattern, url, re.IGNORECASE))


# ======================= Main App =======================
class YouTubeDownloader(QWidget):
    """Main application window for the YouTube Downloader.

    Provides a PyQt5-based GUI with download queue management,
    format selection, and system tray integration.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(400, 100, 800, 550)

        # Frameless window for custom title bar with rounded corners
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_position = None

        # Windows 7 Aero Blue Theme - Authentic Colors
        # Main Windows 7 Blue: #00a2ed (Microsoft Blue)
        # Window Background: #245edc (Classic Windows Blue)
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7bd5, stop:1 #245edc);
                color: #ffffff;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 11px;
                border-radius: 8px;
            }

            QLabel {
                background: transparent;
                color: #ffffff;
                padding: 2px;
            }

            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #7eb4ea;
                border-radius: 3px;
                padding: 5px 8px;
                selection-background-color: #3399ff;
            }

            QLineEdit:focus {
                border: 1px solid #00a2ed;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fefefe, stop:0.4 #e8e8e8, stop:0.5 #d0d0d0, stop:1 #c8c8c8);
                color: #000000;
                border: 1px solid #707070;
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 75px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e5f3fb, stop:0.4 #c4e5f6, stop:0.5 #98d1ef, stop:1 #68c3ea);
                border: 1px solid #3c7fb1;
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d0e9f7, stop:0.4 #a9d9f0, stop:0.5 #7ac2e5, stop:1 #5eb6db);
                border: 1px solid #2c628b;
            }

            QPushButton:disabled {
                background: #f4f4f4;
                color: #838383;
                border: 1px solid #adb2b5;
            }

            QProgressBar {
                background-color: #e6e6e6;
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                text-align: center;
                color: #000000;
                height: 18px;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #37b44a, stop:0.5 #2a9d3c, stop:1 #1e8a30);
                border-radius: 2px;
            }

            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #7eb4ea;
                border-radius: 3px;
                padding: 4px 8px;
                min-width: 120px;
            }

            QComboBox:hover {
                border: 1px solid #00a2ed;
            }

            QComboBox::drop-down {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #d8d8d8);
                width: 20px;
                border-left: 1px solid #c0c0c0;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #3399ff;
                selection-color: white;
                border: 1px solid #7eb4ea;
            }

            QListWidget {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #7eb4ea;
                border-radius: 3px;
                padding: 2px;
            }

            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #e0e0e0;
            }

            QListWidget::item:selected {
                background-color: #3399ff;
                color: white;
            }

            QListWidget::item:hover {
                background-color: #e5f3fb;
            }

            QMessageBox {
                background-color: #f0f0f0;
            }

            QMessageBox QLabel {
                color: #000000;
            }

            QMessageBox QPushButton {
                min-width: 70px;
            }

            /* Green Button - Add/Download actions */
            QPushButton#greenButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb85c, stop:0.5 #449d44, stop:1 #398439);
                color: white;
                border: 1px solid #255625;
                font-weight: bold;
            }

            QPushButton#greenButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6ed36e, stop:0.5 #5cb85c, stop:1 #449d44);
                border: 1px solid #398439;
            }

            QPushButton#greenButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #398439, stop:0.5 #2d6a2d, stop:1 #255625);
            }

            /* Cyan Button - Paste/Fetch actions */
            QPushButton#blueButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00c9d8, stop:0.5 #00a8b8, stop:1 #0090a0);
                color: white;
                border: 1px solid #007080;
                font-weight: bold;
            }

            QPushButton#blueButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20e0f0, stop:0.5 #00c9d8, stop:1 #00a8b8);
                border: 1px solid #0090a0;
            }

            QPushButton#blueButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0090a0, stop:0.5 #007888, stop:1 #006070);
            }

            /* Orange Button - Folder selection */
            QPushButton#orangeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0ad4e, stop:0.5 #ec971f, stop:1 #d58512);
                color: white;
                border: 1px solid #985f0d;
                font-weight: bold;
            }

            QPushButton#orangeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5c879, stop:0.5 #f0ad4e, stop:1 #ec971f);
                border: 1px solid #d58512;
            }

            QPushButton#orangeButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d58512, stop:0.5 #c77c0f, stop:1 #985f0d);
            }

            /* Red Button - Cancel actions */
            QPushButton#redButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d9534f, stop:0.5 #c9302c, stop:1 #ac2925);
                color: white;
                border: 1px solid #761c19;
                font-weight: bold;
            }

            QPushButton#redButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e67573, stop:0.5 #d9534f, stop:1 #c9302c);
                border: 1px solid #ac2925;
            }

            QPushButton#redButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ac2925, stop:0.5 #96231f, stop:1 #761c19);
            }

            QPushButton#redButton:disabled {
                background: #e0a0a0;
                color: #888888;
                border: 1px solid #c08080;
            }

            /* Custom Title Bar */
            QWidget#titleBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90d9, stop:0.5 #2d6fc4, stop:1 #245edc);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                min-height: 32px;
            }

            /* Content Area - matches title bar */
            QWidget#contentArea {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #245edc, stop:1 #1a4a8a);
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }

            QLabel#titleLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding-left: 8px;
            }

            QPushButton#minimizeBtn, QPushButton#maximizeBtn, QPushButton#closeBtn {
                background: transparent;
                border: none;
                color: white;
                font-size: 11px;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 22px;
                max-height: 22px;
                border-radius: 0px;
                padding: 0px;
            }

            QPushButton#minimizeBtn:hover, QPushButton#maximizeBtn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }

            QPushButton#closeBtn:hover {
                background-color: #e81123;
            }

            QPushButton#minimizeBtn:pressed, QPushButton#maximizeBtn:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }

            QPushButton#closeBtn:pressed {
                background-color: #bf0f1d;
            }
        """)

        # Initialize app environment
        self.output_folder = get_download_folder()
        self.db_path = get_database_path()
        init_db(self.db_path)

        # FFmpeg will be loaded lazily on first download (for faster startup)
        self.ffmpeg_path = None

        # ---------------------------------------------------

        # Queue now stores QueueItem objects with metadata
        self.download_queue: list[QueueItem] = []
        self.download_thread = None
        self.downloading = False
        # Track background title fetch threads
        self.title_fetch_threads: list[TitleFetchThread] = []

        self.settings = QSettings("YouTubeDownloader", "Settings")
        # self.output_folder = self.settings.value("output_folder", os.getcwd())

        # Only overwrite output_folder if user has previously saved a folder
        saved_folder = self.settings.value("output_folder")
        if saved_folder:
            self.output_folder = saved_folder

        # -------------video + audio codec number defined here
        # --------------------------Added the format mapping here
        self.format_map = {
            "Mp4-High (720p)": {"video": "136", "audio": "140"},
            "Mp4-HD (1080p)": {"video": "137", "audio": "251"},
            "Mkv-High (720p)": {"video": "247", "audio": "251"},
            "Mkv-HD (1080p)": {"video": "248", "audio": "251"},
            "WebM-High (720p)": {"video": "247", "audio": "251"},
            "WebM-HD (1080p)": {"video": "248", "audio": "251"},
            "Super High WebM": "bestvideo+bestaudio",
            "Audio Only (MP3)": "bestaudio",
        }
        # -------------------------------------------

        self.init_ui()
        self.init_tray()

    # ------------------Shows Dropwnlist format - size------------

    def fetch_format_sizes(self, url):
        """Fetch available format sizes for a given YouTube URL."""
        ydl_opts = {"quiet": True, "skip_download": True}
        formats_list = []

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                info = ydl.extract_info(url, download=False)
                if not info:
                    return []
                formats = info.get("formats", [])

                for f in formats:  # type: ignore[union-attr]
                    fmt_id = f["format_id"]
                    ext = f["ext"]
                    res = f.get("height") or "audio"

                    # Calculate approximate size
                    size = f.get("filesize") or f.get("filesize_approx")
                    if not size:
                        duration = f.get("duration")
                        tbr = f.get("tbr")  # total bitrate in kbps
                        if duration and tbr:
                            size = (
                                duration * tbr * 1000 / 8
                            )  # convert kbps * sec → bytes

                    # ensure numeric
                    size_mb = round(size / (1024 * 1024), 1) if size else 0

                    formats_list.append(
                        {
                            "format_id": fmt_id,
                            "ext": ext,
                            "resolution": res,
                            "size_mb": size_mb,
                        }
                    )
        except (yt_dlp.utils.DownloadError, KeyError, TypeError) as e:
            self.status_label.setText(f"Error fetching formats: {e}")

        return formats_list

    def update_format_dropdown(self):
        """Update the format dropdown with sizes for the current URL."""
        url = self.url_input.text().strip()
        if not url:
            return

        self.format_quality_combo.clear()
        formats_list = self.fetch_format_sizes(url)

        for display_name, codes in self.format_map.items():
            size_mb = 0

            if isinstance(codes, dict) and "video" in codes:
                match = next(
                    (
                        f
                        for f in formats_list
                        if str(f["format_id"]) == str(codes["video"])
                    ),
                    None,
                )
                if match:
                    size_mb = match["size_mb"]

            elif display_name == "Super High WebM":
                largest = max(
                    (f for f in formats_list if f.get("height")),
                    key=lambda x: x["size_mb"]
                    if isinstance(x["size_mb"], (int, float))
                    else 0,
                    default=None,
                )
                if largest:
                    size_mb = largest["size_mb"]

            elif display_name == "Audio Only (MP3)":
                best_audio = max(
                    (
                        f
                        for f in formats_list
                        if str(f["resolution"]).lower() == "audio"
                    ),
                    key=lambda x: x["size_mb"]
                    if isinstance(x["size_mb"], (int, float))
                    else 0,
                    default=None,
                )
                if best_audio:
                    size_mb = best_audio["size_mb"]

            # Show dropdown with size
            display_text = (
                f"{display_name} ~{size_mb} MB"
                if size_mb
                else f"{display_name}     ~Unknown"
            )
            self.format_quality_combo.addItem(display_text)

    # ----------------------- GUI Setup -----------------------
    def init_ui(self):
        """Initialize the user interface components."""
        # --------------Main vertical layout-----------------------
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------------- Custom Title Bar ----------------
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(35)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(5, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        # Title label
        title_label = QLabel("🎬 YouTube Downloader")
        title_label.setObjectName("titleLabel")
        title_bar_layout.addWidget(title_label)

        title_bar_layout.addStretch()

        # Minimize button
        minimize_btn = QPushButton("─")
        minimize_btn.setObjectName("minimizeBtn")
        minimize_btn.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_btn)

        # Maximize button
        self.maximize_btn = QPushButton("☐")
        self.maximize_btn.setObjectName("maximizeBtn")
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        title_bar_layout.addWidget(self.maximize_btn)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.close)
        title_bar_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # Content area with padding - styled to match title bar
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

        # ---------------- URL Input ----------------
        url_content_layout = QHBoxLayout()
        url_content_layout.setSpacing(8)
        content_layout.setContentsMargins(10, 10, 10, 10)
        self.url_input = UrlLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube URL Here")
        # Auto-fetch formats when URL is pasted
        self.url_input.url_pasted.connect(self.update_format_dropdown)
        url_content_layout.addWidget(self.url_input)

        paste_button = QPushButton("📋 Paste URL")
        paste_button.setObjectName("blueButton")
        paste_button.setFixedWidth(100)
        paste_button.setToolTip("Paste URL from clipboard")
        paste_button.clicked.connect(self._paste_clipboard)
        url_content_layout.addWidget(paste_button)
        content_layout.addLayout(url_content_layout)

        # ---------------- Output Folder ----------------
        folder_content_layout = QHBoxLayout()
        folder_content_layout.setSpacing(8)
        self.saved_folder_label = QLabel(f"📁 {self.output_folder}")
        self.saved_folder_label.setToolTip("Current download location")
        folder_content_layout.addWidget(self.saved_folder_label)

        self.output_folder_btn = QPushButton("📂 Change Folder")
        self.output_folder_btn.setObjectName("orangeButton")
        self.output_folder_btn.setFixedWidth(120)
        self.output_folder_btn.setToolTip("Select download folder")
        self.output_folder_btn.clicked.connect(self.select_output_folder)
        folder_content_layout.addWidget(self.output_folder_btn)
        content_layout.addLayout(folder_content_layout)

        # ---------------- Format & Quality ----------------
        format_layout = QHBoxLayout()
        format_layout.setSpacing(8)

        self.format_quality_combo = QComboBox()
        self.format_quality_combo.addItem("🎬 Select Format")
        self.format_quality_combo.setToolTip("Choose video quality and format")
        self.format_quality_combo.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        format_layout.addWidget(self.format_quality_combo)

        # Add a button to fetch formats/sizes
        fetch_button = QPushButton("🔍 Fetch Formats")
        fetch_button.setObjectName("blueButton")
        fetch_button.setToolTip("Get available formats for the URL")
        fetch_button.setFixedWidth(120)
        fetch_button.clicked.connect(self.update_format_dropdown)
        format_layout.addWidget(fetch_button)

        content_layout.addLayout(format_layout)

        # ---------------- Queue Buttons ----------------
        queue_content_layout = QHBoxLayout()
        queue_content_layout.setSpacing(8)

        self.enqueue_button = QPushButton("➕ Add to Queue")
        self.enqueue_button.setObjectName("greenButton")
        self.enqueue_button.setToolTip("Add the URL to download queue")
        self.enqueue_button.clicked.connect(self.enqueue_download)

        self.download_button = QPushButton("▶ Start Download")
        self.download_button.setObjectName("greenButton")
        self.download_button.setToolTip("Start downloading all queued videos")
        self.download_button.clicked.connect(self.start_queue)

        self.cancel_button = QPushButton("⏹ Cancel")
        self.cancel_button.setObjectName("redButton")
        self.cancel_button.setToolTip("Cancel the current download")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)

        queue_content_layout.addWidget(self.enqueue_button)
        queue_content_layout.addWidget(self.download_button)
        queue_content_layout.addWidget(self.cancel_button)
        content_layout.addLayout(queue_content_layout)

        # ---------------- Queue List ----------------
        self.queue_list = QListWidget()
        self.queue_list.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Enable right-click context menu
        self.queue_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.queue_list.customContextMenuRequested.connect(
            self.show_queue_context_menu)
        content_layout.addWidget(self.queue_list)

        # ---------------- Progress Bar ---------------------
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(22)
        self.progress_bar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(self.progress_bar)

        # ---------------- Status Label ----------------
        self.status_label = QLabel("⏸ Ready")
        self.status_label.setContentsMargins(5, 5, 5, 5)
        self.status_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(self.status_label, 0)

        layout.addWidget(content)
        self.setLayout(layout)  # Finalize the layout

    def toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("☐")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")

    def mousePressEvent(self, event):  # pylint: disable=invalid-name
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton and event.pos().y() < 35:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):  # pylint: disable=invalid-name
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, _event):  # pylint: disable=invalid-name
        """Handle mouse release to stop dragging."""
        self.drag_position = None

    def _paste_clipboard(self):
        self.url_input.smart_paste()

    # ----------------------- Tray -----------------------
    def init_tray(self):
        """Initialize the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        style = self.style()
        if style:  # type: ignore[reportOptionalMemberAccess]
            self.tray_icon.setIcon(style.standardIcon(
                QStyle.SP_ComputerIcon))  # type: ignore[attr-defined]

        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        exit_action = QAction("Exit", self)
        restore_action.triggered.connect(
            self.showNormal)  # type: ignore[arg-type]
        exit_action.triggered.connect(self.close)  # type: ignore[arg-type]
        tray_menu.addAction(restore_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(
            self.toggle_visibility)  # type: ignore[arg-type]
        self.tray_icon.show()

    def toggle_visibility(self, reason):
        """Toggle window visibility based on tray icon activation."""
        if reason == QSystemTrayIcon.Trigger:  # type: ignore[attr-defined]
            self.setVisible(not self.isVisible())

    # type: ignore[override]  # pylint: disable=invalid-name
    def closeEvent(self, event):
        """Handle window close event, saving settings."""
        self.settings.setValue("output_folder", self.output_folder)
        self.tray_icon.hide()
        if event:
            event.accept()

    # ----------------------- Folder Selection -----------------------
    def select_output_folder(self):
        """Open a dialog to select the output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.saved_folder_label.setText(f"📁 {self.output_folder}")

    # ----------------------- Queue -----------------------
    def update_queue_display(self):
        """Update the queue list widget to show current queue state."""
        self.queue_list.clear()
        for index, item in enumerate(self.download_queue, start=1):
            icon = item.get_status_icon()
            text = item.get_display_text()
            self.queue_list.addItem(f"#{index} {icon} {text}")

    def fetch_video_title(self, queue_item: QueueItem):
        """Fetch video title in background thread."""
        thread = TitleFetchThread(queue_item.url)
        thread.title_fetched.connect(self.on_title_fetched)
        thread.fetch_failed.connect(self.on_title_fetch_failed)
        thread.finished.connect(
            lambda: self.title_fetch_threads.remove(thread))
        self.title_fetch_threads.append(thread)
        thread.start()

    def on_title_fetched(self, url: str, title: str):
        """Handle successful title fetch."""
        for item in self.download_queue:
            if item.url == url:
                item.title = title
                self.update_queue_display()
                break

    def on_title_fetch_failed(self, url: str, error: str):
        """Handle failed title fetch."""
        for item in self.download_queue:
            if item.url == url:
                item.title = url  # Fallback to showing URL
                self.update_queue_display()
                break

    def show_queue_context_menu(self, position):
        """Show context menu for queue list."""
        if not self.queue_list.itemAt(position):
            return

        menu = QMenu()
        current_row = self.queue_list.currentRow()

        # Remove action
        remove_action = QAction("🗑️ Remove from Queue", self)
        remove_action.triggered.connect(self.remove_selected_from_queue)
        menu.addAction(remove_action)

        menu.addSeparator()

        # Move up/down actions
        move_up_action = QAction("⬆️ Move Up", self)
        move_up_action.triggered.connect(self.move_queue_item_up)
        move_up_action.setEnabled(current_row > 0)
        menu.addAction(move_up_action)

        move_down_action = QAction("⬇️ Move Down", self)
        move_down_action.triggered.connect(self.move_queue_item_down)
        move_down_action.setEnabled(current_row < len(self.download_queue) - 1)
        menu.addAction(move_down_action)

        menu.addSeparator()

        # Clear all action
        clear_action = QAction("🗑️ Clear All", self)
        clear_action.triggered.connect(self.clear_queue)
        menu.addAction(clear_action)

        menu.exec_(self.queue_list.mapToGlobal(position))

    def remove_selected_from_queue(self):
        """Remove the selected item from queue."""
        current_row = self.queue_list.currentRow()
        if 0 <= current_row < len(self.download_queue):
            self.download_queue.pop(current_row)
            self.update_queue_display()

    def move_queue_item_up(self):
        """Move selected queue item up."""
        current_row = self.queue_list.currentRow()
        if current_row > 0:
            self.download_queue[current_row], self.download_queue[current_row - 1] = \
                self.download_queue[current_row -
                                    1], self.download_queue[current_row]
            self.update_queue_display()
            self.queue_list.setCurrentRow(current_row - 1)

    def move_queue_item_down(self):
        """Move selected queue item down."""
        current_row = self.queue_list.currentRow()
        if current_row < len(self.download_queue) - 1:
            self.download_queue[current_row], self.download_queue[current_row + 1] = \
                self.download_queue[current_row +
                                    1], self.download_queue[current_row]
            self.update_queue_display()
            self.queue_list.setCurrentRow(current_row + 1)

    def clear_queue(self):
        """Clear all items from queue."""
        if self.download_queue:
            reply = QMessageBox.question(
                self,
                "Clear Queue",
                "Are you sure you want to clear all items from the queue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.download_queue.clear()
                self.update_queue_display()

    def enqueue_download(self):
        """Add the current URL to the download queue."""
        url = self.url_input.text().strip()
        if not url:
            return

        # Validate URL before adding to queue
        if not validate_url(url):
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Please enter a valid YouTube URL.\n"
                "Supported formats:\n"
                "- https://youtube.com/watch?v=...\n"
                "- https://youtu.be/...\n"
                "- https://youtube.com/shorts/...\n"
                "- https://youtube.com/live/...",
            )
            return

        # Check for duplicates
        if any(item.url == url for item in self.download_queue):
            QMessageBox.warning(
                self,
                "Duplicate URL",
                "This URL is already in the queue.",
            )
            return

        # Get current format selection
        selected_format = self.format_quality_combo.currentText()
        if selected_format.startswith("🎬"):
            selected_format = ""

        # Create queue item
        queue_item = QueueItem(
            url=url,
            title="Fetching title...",
            format_selection=selected_format,
            status=QueueStatus.WAITING
        )

        # Add to queue
        self.download_queue.append(queue_item)

        # Update display
        self.update_queue_display()

        # Fetch title in background
        self.fetch_video_title(queue_item)

        # Clear input
        self.url_input.clear()

    def start_queue(self):
        """Start downloading all items in the queue."""
        if not self.download_queue:
            QMessageBox.information(self, "Info", "No URLs in the queue.")
            return

        if not self.downloading:
            self.download_next()  # Start the first download
            self.cancel_button.setEnabled(True)

    def download_next(self):
        """Download the next URL in the queue."""
        if not self.download_queue:
            self.status_label.setText("Status: All downloads complete.")
            self.downloading = False
            return

        # Pop the next item from the queue
        queue_item = self.download_queue.pop(0)
        url = queue_item.url

        # Update item status
        queue_item.status = QueueStatus.DOWNLOADING
        self.update_queue_display()

        self.status_label.setText(
            f"Status: Downloading {queue_item.title or url}")
        self.downloading = True

        # --- Use new combined dropdown ---
        selected_item = self.format_quality_combo.currentText()
        if "~" in selected_item:
            selected_item = selected_item.split(" ~")[0]  # remove size suffix

        codes = self.format_map.get(selected_item)

        # Lazy-load FFmpeg on first download (speeds up app startup)
        if not self.ffmpeg_path:
            self.ffmpeg_path = find_ffmpeg()

        if not self.ffmpeg_path:
            QMessageBox.warning(
                self,
                "FFmpeg Missing",
                "FFmpeg codec not found.\n"
                "Please click 'Update FFmpeg Codec' to download it.",
            )

        ydl_opts = {
            "outtmpl": os.path.join(self.output_folder, "%(title).200B.%(ext)s"),
            "restrictfilenames": True,  # Sanitize filenames to prevent path traversal
            "quiet": True,
            "noprogress": False,  # enables the progress hooks
            # <-- directory only
            "ffmpeg_location": (
                os.path.dirname(self.ffmpeg_path) if self.ffmpeg_path else None
            ),
            "logger": logger,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "max_retries": 3,
        }

        # --- Map selection to yt-dlp format codes ---
        if selected_item == "Super High WebM":
            ydl_opts["format"] = "bestvideo+bestaudio/best"
        elif selected_item == "Audio Only (MP3)":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            # Use flexible format selection with fallback
            # Instead of hardcoded format IDs, use quality-based selection
            if isinstance(codes, dict):
                # Try specific format codes first, but fall back to quality selector
                video_code = codes.get("video", "")
                audio_code = codes.get("audio", "")

                # Determine target resolution from selection
                if "1080p" in selected_item:
                    quality_fallback = (
                        "bestvideo[height<=1080]+bestaudio/"
                        "best[height<=1080]"
                    )
                elif "720p" in selected_item:
                    quality_fallback = (
                        "bestvideo[height<=720]+bestaudio/"
                        "best[height<=720]"
                    )
                else:
                    quality_fallback = "bestvideo+bestaudio/best"

                # Try specific codes first, then fall back
                if video_code and audio_code:
                    ydl_opts["format"] = f"{video_code}+{audio_code}/{quality_fallback}"
                else:
                    ydl_opts["format"] = quality_fallback

        # Start download thread
        self.download_thread = DownloadThread(url, ydl_opts)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.status.connect(self.status_label.setText)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

    def download_thread_hook(self, d):
        """Hook for yt-dlp progress updates during download."""
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                progress = int(downloaded / total * 100)
                if self.download_thread:
                    self.download_thread.progress.emit(progress)

    def download_finished(self, _success, message, url, title, path, status):
        """Handle download completion and record to history."""
        self.downloading = False
        with DatabaseManager(self.db_path) as db:
            db.record_history(url, title, path, status)
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(False)

        # Check if file already existed
        if "has already been downloaded" in message:
            self.status_label.setText("Status: File already downloaded")
        else:
            self.status_label.setText(f"Status: {message}")

        QTimer.singleShot(100, self.download_next)

    def cancel_download(self):
        """Cancel the currently running download."""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.status_label.setText("Status: Cancel requested...")
            self.cancel_button.setEnabled(False)


# ----------------------- Main -----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
