"""Module for handling smart URL pasting functionality in PyQt5 widgets.

This module provides mixins and custom widgets to validate and paste YouTube URLs
from the clipboard automatically.
"""
# pylint: disable=no-name-in-module
import yt_dlp
from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtGui import QKeyEvent  # type: ignore
from PyQt5.QtWidgets import (  # type: ignore
    QApplication,
    QLineEdit,
    QMessageBox,
    QWidget,
)


class SmartPasteMixin:
    """Mixin to intercept Ctrl+V and validate YouTube URLs."""

    # type: ignore[override]  # pylint: disable=invalid-name
    def keyPressEvent(self, a0: QKeyEvent):
        """Intercept Ctrl+V to validate YouTube URLs."""
        # type: ignore[attr-defined]
        if (a0.modifiers() & Qt.ControlModifier) != 0 and a0.key() == Qt.Key_V:
            clipboard = QApplication.clipboard()
            if clipboard:
                text = clipboard.text()
                if not text.startswith("http"):
                    QMessageBox.warning(
                        # type: ignore[attr-defined]
                        self._get_parent_widget(),
                        "Invalid Paste",
                        "Please paste a valid URL starting with http or https.",
                    )
                    return
        super().keyPressEvent(a0)  # type: ignore[misc]

    def _get_parent_widget(self):  # type: ignore[return]
        """Retrieve the closest QWidget parent."""
        p = self.parent()  # type: ignore[attr-defined]
        while p is not None and not isinstance(p, QWidget):
            p = p.parent()
        return p if isinstance(p, QWidget) else None


class UrlLineEdit(QLineEdit):
    """Custom QLineEdit that performs smart paste validation for YouTube URLs."""
    # Removed redundant __init__

    def keyPressEvent(self, a0: QKeyEvent) -> None:  # pylint: disable=invalid-name
        """Handle key press events to intercept paste shortcuts."""
        # Override Ctrl+V to trigger smart paste instead of normal paste
        # type: ignore[attr-defined]
        if (a0.modifiers() & Qt.ControlModifier) != 0 and a0.key() == Qt.Key_V:
            self.smart_paste()
            return  # Skip default handling
        super().keyPressEvent(a0)

    def smart_paste(self):
        """Check clipboard for a valid URL and insert it if valid.
        Otherwise show a warning.
        """
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
        # type: ignore[attr-defined]
        except (yt_dlp.utils.DownloadError, Exception):  # pylint: disable=broad-exception-caught
            return False

    def _get_parent_widget(self) -> QWidget | None:
        """Retrieve the closest QWidget parent."""
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent
        return None
