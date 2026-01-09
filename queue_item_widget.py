"""Custom queue item widget with clickable remove button."""
from PyQt5.QtCore import pyqtSignal  # type: ignore
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget  # type: ignore


class QueueItemWidget(QWidget):
    """Custom widget for queue list items with clickable remove button."""

    # Signal emitted when remove button is clicked
    remove_clicked = pyqtSignal(int)  # Emits the row index

    def __init__(self, row: int, text: str, parent=None):
        """Initialize queue item widget.

        Args:
            row: Row index in the queue
            text: Display text for the item
            parent: Parent widget
        """
        super().__init__(parent)
        self.row = row

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Remove button (x)
        self.remove_btn = QPushButton("x")
        self.remove_btn.setFixedSize(14, 16)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                color: red;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 14px;
                padding-bottom: 2px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #FFE5E5;
                border-radius: 2px;
            }
        """)
        self.remove_btn.clicked.connect(
            lambda: self.remove_clicked.emit(self.row))
        layout.addWidget(self.remove_btn)

        # Text label
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet(
            "color: black; background-color: transparent;")
        layout.addWidget(self.text_label, 1)  # Stretch factor 1

        self.setLayout(layout)

    def update_text(self, text: str):
        """Update the display text.

        Args:
            text: New text to display
        """
        self.text_label.setText(text)
