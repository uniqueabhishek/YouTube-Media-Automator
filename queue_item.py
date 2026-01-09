"""Queue item data structure for download queue management."""
from dataclasses import dataclass
from enum import Enum


class QueueStatus(Enum):
    """Status of a queue item."""
    WAITING = "waiting"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueItem:
    """Represents a single item in the download queue."""
    url: str
    title: str = ""
    format_selection: str = ""
    status: QueueStatus = QueueStatus.WAITING
    file_size: str = ""
    error_message: str = ""

    def get_display_text(self) -> str:
        """Get formatted display text for the queue list."""
        # Show title if available, otherwise show URL
        display_name = self.title if self.title else self.url

        # Build status line
        parts = []
        if self.format_selection:
            parts.append(f"Format: {self.format_selection}")
        if self.file_size:
            parts.append(f"Size: {self.file_size}")
        parts.append(f"Status: {self.status.value.title()}")

        status_line = " | ".join(parts)

        return f"{display_name}\n       {status_line}"

    def get_status_icon(self) -> str:
        """Get emoji icon for current status."""
        icons = {
            QueueStatus.WAITING: "🟡",
            QueueStatus.DOWNLOADING: "🔵",
            QueueStatus.COMPLETED: "🟢",
            QueueStatus.FAILED: "🔴",
        }
        return icons.get(self.status, "⚪")
