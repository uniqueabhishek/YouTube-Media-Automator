import sys
import os
import re
import yt_dlp

# import subprocess
from download_thread import DownloadThread
from database_handler import setup_database, record_history
from ffmpeg_utils import get_ffmpeg_path as find_ffmpeg
from app_dir_creator import (
    get_download_folder,
    get_database_path,
    ensure_environment,
    download_ffmpeg,
)

from vSmart_Paste_url import UrlLineEdit
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QListWidget,
    QMenu,
    QAction,
    QStyle,
    QSizePolicy,
    QComboBox,
    QSystemTrayIcon,
)  # QLineEdit,
from PyQt5.QtCore import QSettings, QTimer  # QThread, pyqtSignal
from loguru import logger

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
    youtube_pattern = r"^https?://(www\.)?(youtube\.com/(watch\?v=|shorts/|live/|embed/|v/)|youtu\.be/).+"
    return bool(re.match(youtube_pattern, url, re.IGNORECASE))


# ======================= Main App =======================
class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(400, 100, 800, 500)

        # ----Ensure app environment by app_dir_creator.py----
        ffmpeg_path = ensure_environment()
        print("FFmpeg path:", ffmpeg_path)

        download_folder = get_download_folder()
        db_path = get_database_path()

        # Now set as instance variables
        self.ffmpeg_path = ffmpeg_path
        self.output_folder = download_folder
        self.conn, self.db_cursor = setup_database(db_path)

        # ---------------------------------------------------

        self.download_queue = []
        self.download_thread = None
        self.downloading = False

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
        self.check_ffmpeg_on_startup()
        self.init_tray()

    def check_ffmpeg_on_startup(self):
        """Check for FFmpeg on startup using static-ffmpeg package."""
        try:
            self.ffmpeg_path = find_ffmpeg()
            print(f"FFmpeg found at: {self.ffmpeg_path}")
        except Exception as e:
            print(f"FFmpeg error: {e}")
            self.ffmpeg_path = None
            QMessageBox.warning(
                self,
                "FFmpeg Missing",
                f"FFmpeg codec not found: {e}\n"
                "Please check your internet connection.",
            )

    # ------------------Shows Dropwnlist format - size------------
    def fetch_format_sizes(self, url):
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
        except Exception as e:
            self.status_label.setText(f"Error fetching formats: {e}")

        return formats_list

    def update_format_dropdown(self):
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
        # --------------Main vertical layout-----------------------
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)  # Assigns uniform vertical spacing

        # ---------------- URL Input ----------------
        url_layout = QHBoxLayout()
        url_layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        self.url_input = UrlLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube URL Here")
        url_layout.addWidget(self.url_input)

        paste_button = QPushButton("📋 Paste URL")
        paste_button.setFixedWidth(90)
        paste_button.clicked.connect(self._paste_clipboard)
        url_layout.addWidget(paste_button)
        layout.addLayout(url_layout)

        # ---------------- Output Folder ----------------
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(5)
        self.saved_folder_label = QLabel(f"Download to :-  {self.output_folder}")
        folder_layout.addWidget(self.saved_folder_label)

        self.output_folder_btn = QPushButton("Select Download Folder")
        self.output_folder_btn.setFixedWidth(140)
        self.output_folder_btn.clicked.connect(self.select_output_folder)
        folder_layout.addWidget(self.output_folder_btn)
        layout.addLayout(folder_layout)

        # ---------------- Format & Quality ----------------
        self.format_quality_combo = QComboBox()  # Combined format + quality dropdown
        self.format_quality_combo.addItem("Select Format")  # Placeholder
        layout.addWidget(self.format_quality_combo)

        # Add a button to fetch formats/sizes
        fetch_button = QPushButton("Fetch Formats")
        fetch_button.clicked.connect(self.update_format_dropdown)
        layout.addWidget(fetch_button)

        # ---------------- Queue Buttons ----------------
        queue_layout = QHBoxLayout()
        #    queue_layout.setSpacing(5)
        self.enqueue_button = QPushButton("Add to Queue")
        self.enqueue_button.clicked.connect(self.enqueue_download)
        self.download_button = QPushButton("Start Queue Download")
        self.download_button.clicked.connect(self.start_queue)
        self.cancel_button = QPushButton("Cancel Download")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)

        queue_layout.addWidget(self.enqueue_button)
        queue_layout.addWidget(self.download_button)
        queue_layout.addWidget(self.cancel_button)
        layout.addLayout(queue_layout)

        # ---------------- Queue List ----------------
        self.queue_list = QListWidget()
        self.queue_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.queue_list)

        # ---------------- Progress Bar ---------------------
        # progress_layout = QHBoxLayout()  # Isolated layout for progress bar
        # progress_layout.setContentsMargins(0, 0, 0, 0)
        # progress_layout.setSpacing(0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(25)
        #    self.progress_bar.setMaximumWidth(16777215)
        self.progress_bar.setStyleSheet("margin: 0px; padding: 0px;")
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.progress_bar)  # Add directly to main layout

        #    progress_layout.addWidget(self.progress_bar)
        #    layout.addLayout(progress_layout)  # Add the isolated layout
        #    layout.addSpacing(5)
        #    layout.addStretch(0)

        # ---------------- Status Label ----------------
        self.status_label = QLabel("Status: Idle")
        self.status_label.setContentsMargins(0, 0, 0, 0)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.status_label, 0)


        self.setLayout(layout)  # Finalize the layout

    def _paste_clipboard(self):
        self.url_input.smart_paste()

    # ----------------------- Tray -----------------------
    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        style = self.style()
        if style:  # type: ignore[reportOptionalMemberAccess]
            self.tray_icon.setIcon(style.standardIcon(QStyle.SP_ComputerIcon))  # type: ignore[attr-defined]

        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        exit_action = QAction("Exit", self)
        restore_action.triggered.connect(self.showNormal)  # type: ignore[arg-type]
        exit_action.triggered.connect(self.close)  # type: ignore[arg-type]
        tray_menu.addAction(restore_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.toggle_visibility)  # type: ignore[arg-type]
        self.tray_icon.show()

    def toggle_visibility(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # type: ignore[attr-defined]
            self.setVisible(not self.isVisible())

    def closeEvent(self, event):  # type: ignore[override]
        self.settings.setValue("output_folder", self.output_folder)
        self.tray_icon.hide()
        if event:
            event.accept()

    # ----------------------- Folder Selection -----------------------
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.saved_folder_label.setText(f"Download to :-  {self.output_folder}")

    # ----------------------- Queue -----------------------
    def enqueue_download(self):
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

        self.download_queue.append(url)
        self.queue_list.addItem(url)
        self.url_input.clear()

    def start_queue(self):
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

        # Pop the next URL from the queue
        url = self.download_queue.pop(0)
        self.queue_list.takeItem(0)
        self.status_label.setText(f"Status: Downloading {url}")
        self.downloading = True

        # --- Use new combined dropdown ---
        selected_item = self.format_quality_combo.currentText()
        if "~" in selected_item:
            selected_item = selected_item.split(" ~")[0]  # remove size suffix

        codes = self.format_map.get(selected_item)

        self.ffmpeg_path = find_ffmpeg()  # Get FFmpeg path
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
            "ffmpeg_location": os.path.dirname(self.ffmpeg_path) if self.ffmpeg_path else None,
            "logger": logger,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "max_retries": 3,
        }

        # --- Map selection to yt-dlp format codes ---
        if selected_item == "Super High WebM":
            ydl_opts["format"] = "bestvideo+bestaudio"
        elif selected_item == "Audio Only (MP3)":
            ydl_opts["format"] = "bestaudio"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            # Regular video + audio
            if isinstance(codes, dict):
                ydl_opts["format"] = (
                    f"{codes['video']}+{codes['audio']}"
                    if codes.get("audio")
                    else codes["video"]
                )

        # Start download thread
        self.download_thread = DownloadThread(url, ydl_opts)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.status.connect(self.status_label.setText)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

    def download_thread_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                progress = int(downloaded / total * 100)
                if self.download_thread:
                    self.download_thread.progress.emit(progress)

    def download_finished(self, success, message, url, title, path, status):
        self.downloading = False
        record_history(self.db_cursor, self.conn, url, title, path, status)
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(False)

        # Check if file already existed
        if "has already been downloaded" in message:
            self.status_label.setText("Status: File already downloaded")
        else:
            self.status_label.setText(f"Status: {message}")

        QTimer.singleShot(100, self.download_next)

    def cancel_download(self):
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
