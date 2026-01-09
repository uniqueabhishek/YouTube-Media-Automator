import time

import yt_dlp
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    progress = pyqtSignal(int)  # emits 0-100
    status = pyqtSignal(str)  # emits status messages
    finished = pyqtSignal(bool, str, str, str, str, str)
    # success, message, url, title, path, status

    def __init__(self, url, ydl_opts):
        super().__init__()
        self.url = url
        self.ydl_opts = dict(ydl_opts)  # copy to avoid shared mutations
        self._cancelled = False
        self._paused = False

    def run(self):
        def hook(d):
            try:
                if self._cancelled:
                    raise yt_dlp.utils.DownloadCancelled()  # type: ignore[attr-defined]
                # Get total and downloaded bytes
                total = (
                    d.get("total_bytes")
                    or d.get(
                        "total_bytes_estimate",
                    )
                    or 1
                )
                downloaded = d.get("downloaded_bytes", 0)
                # Clamp percent between 0 and 100
                percent = min(max(int(downloaded / total * 100), 0), 100)
                self.progress.emit(percent)  # visual progress bar update
                # self.status.emit(f"Downloading: {percent}%") can delete this line

                # Calculate additional info
                speed = d.get("speed", 0)  # bytes/sec
                eta = d.get("eta", 0)  # seconds remaining

                # Format human-readable
                def format_bytes(b):
                    for unit in ["B", "KB", "MB", "GB"]:
                        if b < 1024:
                            return f"{b:.1f}{unit}"
                        b /= 1024
                    return f"{b:.1f}TB"

                downloaded_str = format_bytes(downloaded)
                total_str = format_bytes(total)
                speed_str = format_bytes(speed) + "/s"
                eta_str = f"{int(eta // 60)}m {int(eta % 60)}s" if eta else "--"

                status_msg = (
                    f"{percent}% | {downloaded_str}/{total_str} "
                    f"| Speed: {speed_str} | ETA: {eta_str}"
                )
                self.status.emit(status_msg)

            except Exception as e:
                self.status.emit(f"Hook error: {e}")

        self.ydl_opts["progress_hooks"] = [hook]

        max_retries = int(self.ydl_opts.pop("max_retries", 3))
        attempt = 0
        while attempt < max_retries:
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:  # type: ignore[arg-type]
                    info = ydl.extract_info(self.url, download=True)
                    if info is None:
                        self.finished.emit(
                            False,
                            "Failed to extract video information",
                            self.url,
                            "",
                            "",
                            "Failed",
                        )
                        return

                    title = info.get("title", "Unknown Title")
                    output_path = ydl.prepare_filename(info)
                    status_text = "Completed"

                self.finished.emit(
                    True,
                    "Download complete!",
                    self.url,
                    title,
                    output_path,
                    status_text,
                )
                return

            except Exception as e:
                attempt += 1
                logger.error(f"Download attempt {attempt} failed for {self.url}: {e}")
                if attempt >= max_retries:
                    self.finished.emit(
                        False,
                        f"Download failed after {max_retries} attempts: {e}",
                        self.url,
                        "",
                        "",
                        "Failed",
                    )
                    return
                time.sleep(3)

    def cancel(self):
        self._cancelled = True
        self.status.emit("Cancelled")
