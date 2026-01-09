"""Queue management module for YouTube Downloader.

This module handles all queue-related operations including display updates,
title fetching, and context menu actions.
"""
from PyQt5.QtCore import QObject, pyqtSignal  # type: ignore
from PyQt5.QtWidgets import QAction, QListWidget, QMenu, QMessageBox  # type: ignore

from queue_item import QueueItem, QueueStatus
from title_fetch_thread import TitleFetchThread


class QueueManager(QObject):
    """Manages the download queue and its UI representation."""

    # Signal emitted when queue is updated
    queue_updated = pyqtSignal()

    def __init__(self, queue_list_widget: QListWidget, parent=None):
        """Initialize queue manager.

        Args:
            queue_list_widget: The QListWidget to display queue items
            parent: Parent QObject
        """
        super().__init__(parent)
        self.queue_list = queue_list_widget
        self.download_queue: list[QueueItem] = []
        self.title_fetch_threads: list[TitleFetchThread] = []

    def update_display(self):
        """Update the queue list widget to show current queue state."""
        self.queue_list.clear()
        for index, item in enumerate(self.download_queue, start=1):
            icon = item.get_status_icon()
            text = item.get_display_text()
            self.queue_list.addItem(f"#{index} {icon} {text}")
        self.queue_updated.emit()

    def add_item(self, queue_item: QueueItem):
        """Add an item to the queue.

        Args:
            queue_item: The QueueItem to add
        """
        self.download_queue.append(queue_item)
        self.update_display()
        self.fetch_video_title(queue_item)

    def fetch_video_title(self, queue_item: QueueItem):
        """Fetch video title in background thread.

        Args:
            queue_item: The queue item to fetch title for
        """
        thread = TitleFetchThread(queue_item.url)
        thread.title_fetched.connect(self.on_title_fetched)
        thread.fetch_failed.connect(self.on_title_fetch_failed)
        thread.finished.connect(
            lambda: self.title_fetch_threads.remove(thread))
        self.title_fetch_threads.append(thread)
        thread.start()

    def on_title_fetched(self, url: str, title: str):
        """Handle successful title fetch.

        Args:
            url: The video URL
            title: The fetched title
        """
        for item in self.download_queue:
            if item.url == url:
                item.title = title
                self.update_display()
                break

    def on_title_fetch_failed(self, url: str, _error: str):
        """Handle failed title fetch.

        Args:
            url: The video URL
            _error: Error message (unused but required by signal)
        """
        for item in self.download_queue:
            if item.url == url:
                item.title = url  # Fallback to showing URL
                self.update_display()
                break

    def show_context_menu(self, position):
        """Show context menu for queue list.

        Args:
            position: Position where menu was requested
        """
        if not self.queue_list.itemAt(position):
            return

        menu = QMenu()
        current_row = self.queue_list.currentRow()

        # Remove action
        remove_action = QAction("🗑️ Remove from Queue", self.queue_list)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)

        menu.addSeparator()

        # Move up/down actions
        move_up_action = QAction("⬆️ Move Up", self.queue_list)
        move_up_action.triggered.connect(self.move_item_up)
        move_up_action.setEnabled(current_row > 0)
        menu.addAction(move_up_action)

        move_down_action = QAction("⬇️ Move Down", self.queue_list)
        move_down_action.triggered.connect(self.move_item_down)
        move_down_action.setEnabled(current_row < len(self.download_queue) - 1)
        menu.addAction(move_down_action)

        menu.addSeparator()

        # Clear all action
        clear_action = QAction("🗑️ Clear All", self.queue_list)
        clear_action.triggered.connect(self.clear_all)
        menu.addAction(clear_action)

        menu.exec_(self.queue_list.mapToGlobal(position))

    def remove_selected(self):
        """Remove the selected item from queue."""
        current_row = self.queue_list.currentRow()
        if 0 <= current_row < len(self.download_queue):
            self.download_queue.pop(current_row)
            self.update_display()

    def move_item_up(self):
        """Move selected queue item up."""
        current_row = self.queue_list.currentRow()
        if current_row > 0:
            self.download_queue[current_row], self.download_queue[current_row - 1] = \
                self.download_queue[current_row -
                                    1], self.download_queue[current_row]
            self.update_display()
            self.queue_list.setCurrentRow(current_row - 1)

    def move_item_down(self):
        """Move selected queue item down."""
        current_row = self.queue_list.currentRow()
        if current_row < len(self.download_queue) - 1:
            self.download_queue[current_row], self.download_queue[current_row + 1] = \
                self.download_queue[current_row +
                                    1], self.download_queue[current_row]
            self.update_display()
            self.queue_list.setCurrentRow(current_row + 1)

    def clear_all(self):
        """Clear all items from queue."""
        if self.download_queue:
            reply = QMessageBox.question(
                self.queue_list,
                "Clear Queue",
                "Are you sure you want to clear all items from the queue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.download_queue.clear()
                self.update_display()

    def has_duplicate(self, url: str) -> bool:
        """Check if URL already exists in queue.

        Args:
            url: URL to check

        Returns:
            True if URL exists in queue
        """
        return any(item.url == url for item in self.download_queue)

    def pop_next(self) -> QueueItem | None:
        """Pop the next item from queue.

        Returns:
            Next QueueItem or None if queue is empty
        """
        if self.download_queue:
            item = self.download_queue.pop(0)
            item.status = QueueStatus.DOWNLOADING
            self.update_display()
            return item
        return None

    def is_empty(self) -> bool:
        """Check if queue is empty.

        Returns:
            True if queue is empty
        """
        return len(self.download_queue) == 0
