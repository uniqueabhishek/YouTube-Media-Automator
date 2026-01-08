from PyQt5.QtWidgets import QLineEdit, QApplication, QMessageBox, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
import yt_dlp


class SmartPasteMixin:
    def keyPressEvent(self, a0: QKeyEvent):  # type: ignore[override]
        if (a0.modifiers() & Qt.ControlModifier) != 0 and a0.key() == Qt.Key_V:  # type: ignore[attr-defined]
            clipboard = QApplication.clipboard()
            if clipboard:
                text = clipboard.text()
                if not text.startswith("http"):
                    QMessageBox.warning(
                        self._get_parent_widget(),  # type: ignore[attr-defined]
                        "Invalid Paste",
                        "Please paste a valid URL starting with http or https.",
                    )
                    return
        super().keyPressEvent(a0)  # type: ignore[misc]

    def _get_parent_widget(self):  # type: ignore[return]
        p = self.parent()  # type: ignore[attr-defined]
        while p is not None and not isinstance(p, QWidget):
            p = p.parent()
        return p if isinstance(p, QWidget) else None


class UrlLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        # Override Ctrl+V to trigger smart paste instead of normal paste
        if (a0.modifiers() & Qt.ControlModifier) != 0 and a0.key() == Qt.Key_V:  # type: ignore[attr-defined]
            self.smart_paste()
            return  # Skip default handling
        super().keyPressEvent(a0)

    def smart_paste(self):
        """Check clipboard for a valid URL and insert it if valid. Otherwise show a warning."""
        clipboard = QApplication.clipboard()
        if not clipboard:
            return
        text = clipboard.text().strip()

        if text and self._is_valid_url(text):
            self.setText(text)
        else:
            QMessageBox.warning(
                self._get_parent_widget(),
                "Invalid URL",
                "No valid URL found in clipboard.",
            )

    def _is_valid_url(self, text: str) -> bool:
        """Use yt-dlp to validate URL quickly."""
        ydl_opts = {"quiet": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                ydl.extract_info(text, download=False)
            return True
        except yt_dlp.utils.DownloadError:  # type: ignore[attr-defined]
            return False
        except Exception:
            return False

    def _get_parent_widget(self) -> QWidget | None:
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent
        return None
