"""Module for handling smart URL pasting functionality in PyQt5 widgets.

This module provides custom widgets to validate and paste YouTube URLs
from the clipboard automatically.
"""
# pylint: disable=no-name-in-module
import re
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal  # type: ignore
from PyQt5.QtGui import QKeyEvent  # type: ignore
from PyQt5.QtWidgets import (  # type: ignore
    QApplication,
    QLineEdit,
    QMessageBox,
    QWidget,
)


class UrlLineEdit(QLineEdit):
    """Custom QLineEdit that performs smart paste validation for YouTube URLs."""

    # Signal emitted when a valid URL is pasted
    url_pasted = pyqtSignal()

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
            # Emit signal to trigger auto-fetch of formats
            self.url_pasted.emit()
        else:
            QMessageBox.warning(
                self._get_parent_widget(),
                "Invalid URL",
                "No valid YouTube URL found in clipboard.\n"
                "Please copy a link starting with 'http' or 'https'.",
            )

    def _is_valid_url(self, text: str) -> bool:
        """Validate if the URL looks like a YouTube URL using Regex.

        This avoids the heavy network overhead of initializing yt-dlp.
        """
        # Basic check for http/https
        if not text.lower().startswith(("http://", "https://")):
            return False

        # Optional: More ergonomic check for YouTube domains
        # (Matches standard validation logic in main_window.py)
        youtube_pattern = (
            r"^https?://(www\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|v/)|youtu\.be/).+"
        )
        return bool(re.match(youtube_pattern, text, re.IGNORECASE))

    def _get_parent_widget(self) -> Optional[QWidget]:
        """Retrieve the closest QWidget parent."""
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent
        return None
