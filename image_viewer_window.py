from __future__ import annotations

import os
import platform
import sys
from typing import List, Optional, Tuple

from PIL import Image, UnidentifiedImageError
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, QRect, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constants import (
    APP_DISPLAY_NAME,
    APP_NAME,
    CONTROL_FADE_DURATION_MS,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    FRAME_RESIZE_MARGIN,
    FULLSCREEN_IDLE_HIDE_MS,
    INITIAL_WINDOW_SCREEN_RATIO,
    MAX_CACHE_SIZE,
    MAX_MEMORY_MB,
    MAX_RESIZE_CACHE_SIZE,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    RESIZE_DEBOUNCE_MS,
)
from file_association import register_file_associations
from image_cache import ImageCache
from utils import file_signature, get_current_image_index, get_image_files_from_directory, is_image_file

IS_WINDOWS = platform.system() == "Windows"

DEFAULT_CONTAINER_SIZE = (640, 480)
PLACEHOLDER_TEXT = "이미지를 드래그하거나 Ctrl+O로 열어보세요"

STYLE = (
    "QMainWindow { background-color: #121212; }"
    "#ImageContainer { background-color: #000000; }"
    "#TitleBar { background-color: #1e1e1e; border-bottom: 1px solid #333; }"
    "#ControlBar { background-color: rgba(30, 30, 30, 220); border-top: 1px solid #333; }"
    "QPushButton { background: transparent; color: #eee; border: none; "
    "font-size: 14px; padding: 5px; outline: none; }"
    "QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }"
    "QPushButton:pressed { background-color: rgba(255, 255, 255, 0.2); }"
    "QPushButton:focus { background: transparent; }"
    "QPushButton:disabled { color: #555; background: transparent; }"
    "QLabel { color: #aaa; font-size: 12px; }"
    "#TitleLabel { color: #eee; font-weight: bold; }"
    "#ImagePlaceholder { color: #666; font-size: 14px; }"
    "QMenu { background-color: #1e1e1e; color: #eee; border: 1px solid #333; }"
    "QMenu::item { background-color: transparent; padding: 6px 20px; }"
    "QMenu::item:selected { background-color: rgba(255, 255, 255, 0.1); }"
    "QMenu::separator { height: 1px; background: #333; margin: 4px 0; }"
    "QMessageBox { background-color: #1e1e1e; }"
    "QMessageBox QLabel { color: #eee; font-size: 13px; }"
    "QMessageBox QPushButton {"
    " background-color: #2d2d2d; color: #eee; border: 1px solid #555;"
    " border-radius: 4px; min-width: 72px; min-height: 28px; padding: 2px 12px; }"
    "QMessageBox QPushButton:hover { background-color: #3a3a3a; }"
    "QMessageBox QPushButton:pressed { background-color: #454545; }"
    "QMessageBox QPushButton:default { border: 2px solid #3578e5; }"
)

_EDGE_CURSORS = {
    "left": Qt.CursorShape.SizeHorCursor,
    "right": Qt.CursorShape.SizeHorCursor,
    "top": Qt.CursorShape.SizeVerCursor,
    "bottom": Qt.CursorShape.SizeVerCursor,
    "top_left": Qt.CursorShape.SizeFDiagCursor,
    "bottom_right": Qt.CursorShape.SizeFDiagCursor,
    "top_right": Qt.CursorShape.SizeBDiagCursor,
    "bottom_left": Qt.CursorShape.SizeBDiagCursor,
}


class _ImageLoadSignals(QObject):
    loaded = Signal(int, str, QImage)
    error = Signal(int, str)


class _ImageLoadTask(QRunnable):
    """백그라운드 스레드에서 이미지를 로드·리사이즈한다.

    QPixmap은 GUI 스레드에서만 안전하게 만들 수 있어, 워커는 스레드 세이프한
    QImage까지만 만들고 QPixmap 변환은 메인 스레드의 슬롯에서 수행한다.
    """

    def __init__(self, seq: int, file_path: str, target_size: Tuple[int, int], raw_cache: ImageCache):
        super().__init__()
        self.signals = _ImageLoadSignals()
        self._seq = seq
        self._file_path = file_path
        self._target_size = target_size
        self._raw_cache = raw_cache

    def run(self) -> None:
        try:
            signature = file_signature(self._file_path)
            cache_key = f"{self._file_path}::{signature}"

            image = self._raw_cache.get(cache_key)
            if image is None:
                with Image.open(self._file_path) as opened:
                    image = opened.copy()
                self._raw_cache.put(cache_key, image)

            resized = self._resize_to_fit(image, *self._target_size)
            if resized.mode not in ("RGB", "RGBA", "L"):
                resized = resized.convert("RGBA")

            qimage = ImageQt(resized).copy()  # copy()로 PIL 버퍼에서 완전히 분리
            self.signals.loaded.emit(self._seq, self._file_path, qimage)
        except (UnidentifiedImageError, OSError) as e:
            self.signals.error.emit(self._seq, f"이미지를 열 수 없습니다: {self._file_path}\n{e}")
        except Exception as e:
            self.signals.error.emit(self._seq, f"이미지 표시 중 오류 발생: {e}")

    @staticmethod
    def _resize_to_fit(image: Image.Image, box_width: int, box_height: int) -> Image.Image:
        image_ratio = image.width / image.height
        box_ratio = box_width / box_height
        if image_ratio > box_ratio:
            new_width, new_height = box_width, max(1, int(box_width / image_ratio))
        else:
            new_height, new_width = box_height, max(1, int(box_height * image_ratio))
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


class ImageViewerWindow(QMainWindow):
    def __init__(self, initial_file: Optional[str] = None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(STYLE)
        self.setAcceptDrops(True)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(*self._initial_window_size())

        self.images: List[str] = []
        self.current_index: int = 0
        self.current_pixmap: Optional[QPixmap] = None
        self.current_path: Optional[str] = None

        self.raw_cache = ImageCache(max_size=MAX_CACHE_SIZE, max_memory_mb=MAX_MEMORY_MB)
        self.resize_cache: "dict[str, QImage]" = {}
        self.thread_pool = QThreadPool.globalInstance()

        self._load_seq = 0
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(RESIZE_DEBOUNCE_MS)
        self._resize_timer.timeout.connect(self._on_resize_settled)

        self._drag_pos = None
        self._resize_edge: Optional[str] = None
        self._resize_start_geometry: Optional[QRect] = None
        self._resize_start_global_pos = None

        self._build_ui()
        self._init_fade_animations()

        self.mouse_timer = QTimer(self)
        self.mouse_timer.setInterval(FULLSCREEN_IDLE_HIDE_MS)
        self.mouse_timer.setSingleShot(True)
        self.mouse_timer.timeout.connect(self._hide_controls_on_timeout)

        self.setMouseTracking(True)
        for widget in (self.central_widget, self.image_container, self.image_label, self.title_bar, self.control_bar):
            widget.setMouseTracking(True)
            widget.installEventFilter(self)

        self.setFocus()

        if initial_file and os.path.isfile(initial_file):
            QTimer.singleShot(0, self, lambda path=initial_file: self.open_file(path))

    # ------------------------------------------------------------------
    # UI 구성
    # ------------------------------------------------------------------
    def _initial_window_size(self) -> Tuple[int, int]:
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if screen is None:
            return DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
        geo = screen.availableGeometry()
        width = max(MIN_WINDOW_WIDTH, min(DEFAULT_WINDOW_WIDTH, int(geo.width() * INITIAL_WINDOW_SCREEN_RATIO)))
        height = max(MIN_WINDOW_HEIGHT, min(DEFAULT_WINDOW_HEIGHT, int(geo.height() * INITIAL_WINDOW_SCREEN_RATIO)))
        return width, height

    def _build_ui(self) -> None:
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = QFrame()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(35)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(15, 0, 0, 0)

        self.title_label = QLabel(APP_DISPLAY_NAME)
        self.title_label.setObjectName("TitleLabel")
        title_bar_layout.addWidget(self.title_label)
        title_bar_layout.addStretch()

        self.min_btn = QPushButton("-")
        self.min_btn.setFixedSize(40, 35)
        self.min_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("x")
        self.close_btn.setFixedSize(40, 35)
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("QPushButton:hover { background-color: #e81123; color: white; }")

        title_bar_layout.addWidget(self.min_btn)
        title_bar_layout.addWidget(self.close_btn)
        self.main_layout.addWidget(self.title_bar)

        self.image_container = QFrame()
        self.image_container.setObjectName("ImageContainer")
        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel(PLACEHOLDER_TEXT)
        self.image_label.setObjectName("ImagePlaceholder")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.image_container, 1)

        self.control_bar = QFrame()
        self.control_bar.setObjectName("ControlBar")
        self.control_bar.setFixedHeight(60)
        control_layout = QHBoxLayout(self.control_bar)
        control_layout.setContentsMargins(15, 5, 15, 5)
        control_layout.setSpacing(10)

        self.open_btn = QPushButton("Open")
        self.open_btn.setFixedSize(60, 35)
        self.open_btn.setToolTip("Open Image File (Ctrl+O)")
        self.open_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.open_btn.clicked.connect(self.select_image)
        control_layout.addWidget(self.open_btn)

        self.prev_btn = QPushButton("|<")
        self.prev_btn.setFixedSize(45, 35)
        self.prev_btn.setToolTip("Previous Image (←)")
        self.prev_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.show_previous_image)
        control_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton(">|")
        self.next_btn.setFixedSize(45, 35)
        self.next_btn.setToolTip("Next Image (→)")
        self.next_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.show_next_image)
        control_layout.addWidget(self.next_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedSize(70, 35)
        self.delete_btn.setToolTip("Delete Current Image (Del)")
        self.delete_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_current_image)
        control_layout.addWidget(self.delete_btn)

        self.counter_label = QLabel("0 / 0")
        self.counter_label.setFixedHeight(35)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.counter_label)

        self.filename_label = QLabel("")
        self.filename_label.setFixedHeight(35)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        control_layout.addWidget(self.filename_label, 1)

        self.main_layout.addWidget(self.control_bar)

    def _init_fade_animations(self) -> None:
        """전체 화면에서 유휴 상태일 때 타이틀/컨트롤 바를 부드럽게 숨기기 위한 애니메이션."""
        self._title_opacity = QGraphicsOpacityEffect(self.title_bar)
        self._title_opacity.setOpacity(1.0)
        self.title_bar.setGraphicsEffect(self._title_opacity)

        self._control_opacity = QGraphicsOpacityEffect(self.control_bar)
        self._control_opacity.setOpacity(1.0)
        self.control_bar.setGraphicsEffect(self._control_opacity)

        self._title_fade_anim = QPropertyAnimation(self._title_opacity, b"opacity", self)
        self._title_fade_anim.setDuration(CONTROL_FADE_DURATION_MS)
        self._title_fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._title_fade_anim.finished.connect(lambda: self._on_fade_finished(self.title_bar, self._title_opacity))

        self._control_fade_anim = QPropertyAnimation(self._control_opacity, b"opacity", self)
        self._control_fade_anim.setDuration(CONTROL_FADE_DURATION_MS)
        self._control_fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._control_fade_anim.finished.connect(lambda: self._on_fade_finished(self.control_bar, self._control_opacity))

    def _on_fade_finished(self, widget: QWidget, effect: QGraphicsOpacityEffect) -> None:
        if effect.opacity() <= 0.01:
            widget.hide()

    def _fade_widget_in(self, widget: QWidget, effect: QGraphicsOpacityEffect, anim: QPropertyAnimation) -> None:
        anim.stop()
        if not widget.isVisible():
            effect.setOpacity(0.0)
            widget.show()
        anim.setStartValue(effect.opacity())
        anim.setEndValue(1.0)
        anim.start()

    def _fade_widget_out(self, widget: QWidget, effect: QGraphicsOpacityEffect, anim: QPropertyAnimation) -> None:
        if not widget.isVisible():
            return
        anim.stop()
        anim.setStartValue(effect.opacity())
        anim.setEndValue(0.0)
        anim.start()

    # ------------------------------------------------------------------
    # 파일 열기 / 탐색
    # ------------------------------------------------------------------
    def select_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 파일 열기",
            "",
            "이미지 파일 (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.tif);;모든 파일 (*)",
        )
        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path: str) -> None:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            self.show_error(f"파일이 존재하지 않습니다: {file_path}")
            return
        if not is_image_file(file_path):
            self.show_error(f"지원되지 않는 파일 형식입니다: {file_path}")
            return

        directory = os.path.dirname(file_path)
        self.images = get_image_files_from_directory(directory)
        self.current_index = get_current_image_index(self.images, file_path)
        self.show_image(self.current_index)

    def show_image(self, index: int) -> None:
        if not self.images or index < 0 or index >= len(self.images):
            return
        self.current_index = index
        file_path = self.images[index]

        width = self.image_container.width() or DEFAULT_CONTAINER_SIZE[0]
        height = self.image_container.height() or DEFAULT_CONTAINER_SIZE[1]

        self._load_seq += 1
        seq = self._load_seq

        signature = file_signature(file_path)
        cache_key = f"{file_path}::{signature}::{width}x{height}"
        cached = self.resize_cache.get(cache_key)
        if cached is not None:
            self._apply_image(seq, file_path, cached)
            self._update_nav_state()
            return

        self._show_loading_indicator()

        task = _ImageLoadTask(seq, file_path, (width, height), self.raw_cache)
        task.signals.loaded.connect(self._on_image_loaded)
        task.signals.error.connect(self._on_image_error)
        self.thread_pool.start(task)
        self._update_nav_state()

    def _on_image_loaded(self, seq: int, file_path: str, qimage: QImage) -> None:
        if seq != self._load_seq:
            return
        width = self.image_container.width() or DEFAULT_CONTAINER_SIZE[0]
        height = self.image_container.height() or DEFAULT_CONTAINER_SIZE[1]
        signature = file_signature(file_path)
        cache_key = f"{file_path}::{signature}::{width}x{height}"

        if len(self.resize_cache) >= MAX_RESIZE_CACHE_SIZE and cache_key not in self.resize_cache:
            oldest_key = next(iter(self.resize_cache))
            del self.resize_cache[oldest_key]
        self.resize_cache[cache_key] = qimage

        self._apply_image(seq, file_path, qimage)

    def _apply_image(self, seq: int, file_path: str, qimage: QImage) -> None:
        if seq != self._load_seq:
            return
        pixmap = QPixmap.fromImage(qimage)
        self.current_pixmap = pixmap
        self.current_path = file_path
        self.image_label.setObjectName("")
        self.image_label.setStyleSheet("")
        self.image_label.setPixmap(pixmap)
        self.title_label.setText(f"{APP_DISPLAY_NAME} - {os.path.basename(file_path)}")
        self.counter_label.setText(f"{self.current_index + 1} / {len(self.images)}")
        self.filename_label.setText(os.path.basename(file_path))

    def _on_image_error(self, seq: int, message: str) -> None:
        if seq != self._load_seq:
            return
        self.show_error(message)

    def _show_loading_indicator(self) -> None:
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("로딩 중...")

    def _update_nav_state(self) -> None:
        has_images = bool(self.images)
        self.prev_btn.setEnabled(has_images and self.current_index > 0)
        self.next_btn.setEnabled(has_images and self.current_index < len(self.images) - 1)
        self.delete_btn.setEnabled(has_images)

    def show_next_image(self) -> None:
        if self.images and self.current_index < len(self.images) - 1:
            self.show_image(self.current_index + 1)

    def show_previous_image(self) -> None:
        if self.images and self.current_index > 0:
            self.show_image(self.current_index - 1)

    # ------------------------------------------------------------------
    # 창 크기 변경 / 전체 화면
    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.current_pixmap is not None:
            self._resize_timer.start()

    def _on_resize_settled(self) -> None:
        self.resize_cache.clear()
        if self.images:
            self.show_image(self.current_index)

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self._restore_bars()
        else:
            self.showFullScreen()
            self.handle_mouse_activity()

    def _restore_bars(self) -> None:
        self._title_fade_anim.stop()
        self._control_fade_anim.stop()
        self._title_opacity.setOpacity(1.0)
        self._control_opacity.setOpacity(1.0)
        self.title_bar.show()
        self.control_bar.show()
        self.unsetCursor()
        self.mouse_timer.stop()

    def handle_mouse_activity(self) -> None:
        if self.isFullScreen():
            self.unsetCursor()
            self._fade_widget_in(self.title_bar, self._title_opacity, self._title_fade_anim)
            self._fade_widget_in(self.control_bar, self._control_opacity, self._control_fade_anim)
            self.mouse_timer.start()

    def _hide_controls_on_timeout(self) -> None:
        if not self.isFullScreen():
            return
        pos = self.mapFromGlobal(self.cursor().pos())
        if self.control_bar.geometry().contains(pos) or self.title_bar.geometry().contains(pos):
            self.mouse_timer.start()
            return
        self._fade_widget_out(self.title_bar, self._title_opacity, self._title_fade_anim)
        self._fade_widget_out(self.control_bar, self._control_opacity, self._control_fade_anim)
        self.setCursor(Qt.CursorShape.BlankCursor)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.MouseMove:
            self.handle_mouse_activity()
        return super().eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child in (self.image_container, self.image_label, self.central_widget):
                self.toggle_fullscreen()
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    # ------------------------------------------------------------------
    # 프레임리스 창 이동 / 가장자리 크기 조절
    # ------------------------------------------------------------------
    def _edge_at(self, local_pos) -> Optional[str]:
        """프레임리스 창에서 OS 테두리를 대신할 가장자리 감지.

        local_pos는 self 기준 좌표여야 하며, 창 여백 FRAME_RESIZE_MARGIN px
        이내일 때만 해당 방향의 리사이즈 엣지를 반환한다.
        """
        rect = self.rect()
        margin = FRAME_RESIZE_MARGIN
        left = local_pos.x() <= margin
        right = local_pos.x() >= rect.width() - margin
        top = local_pos.y() <= margin
        bottom = local_pos.y() >= rect.height() - margin

        if top and left:
            return "top_left"
        if top and right:
            return "top_right"
        if bottom and left:
            return "bottom_left"
        if bottom and right:
            return "bottom_right"
        if left:
            return "left"
        if right:
            return "right"
        if top:
            return "top"
        if bottom:
            return "bottom"
        return None

    def _resize_by_edge(self, edge: str, global_pos) -> None:
        delta = global_pos - self._resize_start_global_pos
        geo = QRect(self._resize_start_geometry)
        min_w, min_h = self.minimumWidth(), self.minimumHeight()

        if "left" in edge:
            geo.setLeft(min(geo.left() + delta.x(), geo.right() - min_w + 1))
        if "right" in edge:
            geo.setRight(max(geo.right() + delta.x(), geo.left() + min_w - 1))
        if "top" in edge:
            geo.setTop(min(geo.top() + delta.y(), geo.bottom() - min_h + 1))
        if "bottom" in edge:
            geo.setBottom(max(geo.bottom() + delta.y(), geo.top() + min_h - 1))

        self.setGeometry(geo)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.isFullScreen():
            local_pos = self.mapFromGlobal(event.globalPosition().toPoint())
            edge = self._edge_at(local_pos)
            if edge:
                self._resize_edge = edge
                self._resize_start_geometry = self.geometry()
                self._resize_start_global_pos = event.globalPosition().toPoint()
                event.accept()
                return

            child = self.childAt(local_pos)
            draggable = {
                self.image_container, self.image_label, self.central_widget,
                self.title_bar, self.control_bar,
                self.title_label, self.counter_label, self.filename_label,
            }
            if child is None or child in draggable:
                self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._resize_edge is not None:
            self._resize_by_edge(self._resize_edge, event.globalPosition().toPoint())
            return
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()
        elif not self.isFullScreen() and event.buttons() == Qt.MouseButton.NoButton:
            local_pos = self.mapFromGlobal(event.globalPosition().toPoint())
            edge = self._edge_at(local_pos)
            if edge:
                self.setCursor(_EDGE_CURSORS[edge])
            else:
                self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._resize_edge = None
        self._resize_start_geometry = None
        self._resize_start_global_pos = None
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # 키보드 단축키
    # ------------------------------------------------------------------
    def keyPressEvent(self, event) -> None:
        key = event.key()
        # Qt는 macOS에서 ControlModifier를 Cmd 키에 매핑해 표준화하므로,
        # 별도의 플랫폼 분기 없이 Ctrl+O 등을 그대로 사용할 수 있다.
        ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

        if key == Qt.Key.Key_Left:
            self.show_previous_image()
        elif key == Qt.Key.Key_Right:
            self.show_next_image()
        elif key in (Qt.Key.Key_Space, Qt.Key.Key_Escape):
            self.close()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.toggle_fullscreen()
        elif ctrl and key == Qt.Key.Key_O:
            self.select_image()
        elif ctrl and key == Qt.Key.Key_R:
            self.clear_cache()
        elif ctrl and key == Qt.Key.Key_M:
            self.show_memory_info()
        elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.delete_current_image()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # 드래그 앤 드롭
    # ------------------------------------------------------------------
    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            if files and is_image_file(files[0]):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event) -> None:
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.open_file(files[0])

    # ------------------------------------------------------------------
    # 우클릭 메뉴
    # ------------------------------------------------------------------
    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)

        open_action = QAction("Open Image...", self)
        open_action.triggered.connect(self.select_image)
        menu.addAction(open_action)
        menu.addSeparator()

        delete_action = QAction("Delete Current Image", self)
        delete_action.setEnabled(bool(self.current_path))
        delete_action.triggered.connect(self.delete_current_image)
        menu.addAction(delete_action)

        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.triggered.connect(self.clear_cache)
        menu.addAction(clear_cache_action)

        memory_action = QAction("Memory Info", self)
        memory_action.triggered.connect(self.show_memory_info)
        menu.addAction(memory_action)
        menu.addSeparator()

        if IS_WINDOWS:
            register_action = QAction("Set as Default Image Viewer", self)
            register_action.triggered.connect(self.setup_default_program)
            menu.addAction(register_action)
            menu.addSeparator()

        debug_action = QAction("Debug Info", self)
        debug_action.triggered.connect(self.show_debug_info)
        menu.addAction(debug_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

        menu.exec(event.globalPos())

    # ------------------------------------------------------------------
    # 캐시 / 정보 / 파일 연결
    # ------------------------------------------------------------------
    def clear_cache(self) -> None:
        self.raw_cache.clear()
        self.resize_cache.clear()
        QMessageBox.information(self, "캐시 정리", "모든 캐시가 정리되었습니다.")

    def show_memory_info(self) -> None:
        stats = self.raw_cache.get_stats()
        info = (
            f"이미지 캐시:\n"
            f"  - 캐시된 이미지: {stats['size']}/{stats['max_size']}\n"
            f"  - 메모리 사용량: {stats['memory_usage_mb']:.2f}MB/{stats['max_memory_mb']}MB\n"
            f"리사이즈 캐시:\n"
            f"  - 캐시된 리사이즈: {len(self.resize_cache)}/{MAX_RESIZE_CACHE_SIZE}"
        )
        QMessageBox.information(self, "메모리 정보", info)

    def show_debug_info(self) -> None:
        stats = self.raw_cache.get_stats()
        info = (
            f"OS: {platform.system()}\n"
            f"Python 버전: {sys.version}\n"
            f"현재 작업 디렉토리: {os.getcwd()}\n"
            f"이미지 파일 수: {len(self.images)}\n"
            f"현재 이미지 인덱스: {self.current_index}\n"
            f"캐시된 이미지: {stats['size']}/{stats['max_size']}\n"
            f"메모리 사용량: {stats['memory_usage_mb']:.2f}MB\n"
        )
        if self.current_path:
            info += f"현재 이미지: {self.current_path}\n"
        QMessageBox.information(self, "디버그 정보", info)

    def setup_default_program(self) -> None:
        success = register_file_associations(silent=True)
        if not success:
            QMessageBox.warning(
                self,
                "오류",
                "레지스트리 등록 중 오류가 발생했습니다.\n백신 프로그램이 레지스트리 쓰기를 차단하고 있는지 확인해주세요.",
            )
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("기본 프로그램 설정")
        msg_box.setText(
            "ImageViewer가 파일 연결 목록에 등록되었습니다.\n\n"
            "Windows 정책상 설정 앱에서 직접 기본 앱으로 선택해야 적용됩니다.\n\n"
            "OK를 누르면 Windows '기본 앱' 설정 화면이 열립니다.\n"
            "'ImageViewer'를 검색해 기본 앱으로 지정해주세요."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg_box.setButtonText(QMessageBox.StandardButton.Yes, "OK (설정 열기)")
        msg_box.setButtonText(QMessageBox.StandardButton.No, "취소")

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                os.startfile(f"ms-settings:defaultapps?registeredApp={APP_NAME}")
            except Exception:
                try:
                    os.startfile("ms-settings:defaultapps")
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "실행 실패",
                        f"설정 화면을 여는 데 실패했습니다:\n{e}\n\nWindows 시작 메뉴에서 '기본 앱'을 직접 검색해주세요.",
                    )

    def delete_current_image(self) -> None:
        if not self.current_path:
            QMessageBox.information(self, "삭제 불가", "삭제할 이미지가 없습니다.")
            return

        file_to_delete = self.current_path
        file_name = os.path.basename(file_to_delete)

        confirm = QMessageBox.question(
            self,
            "이미지 삭제 확인",
            f"'{file_name}' 파일을 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            os.remove(file_to_delete)
        except OSError as e:
            QMessageBox.critical(
                self,
                "삭제 오류",
                f"파일 삭제 실패: {file_name}\n{e}\n\n파일이 사용 중이거나 권한이 없을 수 있습니다.",
            )
            return

        QMessageBox.information(self, "삭제 완료", f"'{file_name}' 파일이 성공적으로 삭제되었습니다.")

        if file_to_delete in self.images:
            self.images.remove(file_to_delete)
        self.raw_cache.clear()
        self.resize_cache.clear()

        if self.images:
            self.current_index = min(self.current_index, len(self.images) - 1)
            self.show_image(self.current_index)
        else:
            self._load_seq += 1  # 대기 중인 결과를 모두 폐기
            self.current_pixmap = None
            self.current_path = None
            self.image_label.setObjectName("ImagePlaceholder")
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(PLACEHOLDER_TEXT)
            self.title_label.setText(APP_DISPLAY_NAME)
            self.counter_label.setText("0 / 0")
            self.filename_label.setText("")
            self._update_nav_state()
            QMessageBox.information(self, "알림", "더 이상 표시할 이미지가 없습니다.")

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "오류", message)
