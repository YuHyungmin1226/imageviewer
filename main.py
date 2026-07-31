from __future__ import annotations

import os
import sys
from collections.abc import Callable
from typing import Optional

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtGui import QFileOpenEvent
from PySide6.QtWidgets import QApplication


class ImageViewerApplication(QApplication):
    """macOS의 OS 레벨 파일 열기 요청을 뷰어 준비 완료 후 전달한다."""

    def __init__(self, argv: list[str]) -> None:
        self._file_open_handler: Optional[Callable[[str], None]] = None
        self._pending_file_opens: list[str] = []
        super().__init__(argv)

    def event(self, event) -> bool:
        if event.type() == QEvent.Type.FileOpen:
            path = event.file() if isinstance(event, QFileOpenEvent) else ""
            if path:
                if self._file_open_handler:
                    self._file_open_handler(path)
                else:
                    self._pending_file_opens.append(path)
            return True
        return super().event(event)

    def set_file_open_handler(self, handler: Callable[[str], None]) -> None:
        self._file_open_handler = handler
        pending, self._pending_file_opens = self._pending_file_opens, []
        for path in pending:
            handler(path)


def main() -> int:
    app = ImageViewerApplication(sys.argv)
    app.setStyle("Fusion")

    from image_viewer_window import ImageViewerWindow

    initial_file = None
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        initial_file = sys.argv[1]

    window = ImageViewerWindow(initial_file)
    window.setAcceptDrops(True)
    window.show()

    scheduled_paths: set[str] = set()

    def schedule_file_open(file_path: str) -> None:
        normalized = os.path.normcase(os.path.abspath(file_path))
        if normalized in scheduled_paths:
            return
        scheduled_paths.add(normalized)

        def load_scheduled_file() -> None:
            scheduled_paths.discard(normalized)
            window.open_file(file_path)

        QTimer.singleShot(100, window, load_scheduled_file)

    app.set_file_open_handler(schedule_file_open)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
