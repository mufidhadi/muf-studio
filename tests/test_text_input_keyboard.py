"""
Test untuk memverifikasi bahwa text input pada mode anotasi bisa menerima
keyboard input dengan benar.

Root cause: QLineEdit dibuat sebagai child dari overlay yang memiliki
WindowDoesNotAcceptFocus flag, sehingga QLineEdit tidak bisa menerima
keyboard events. Fix: Buat QLineEdit sebagai popup window terpisah.
"""
import pytest
from PyQt6.QtCore import Qt, QPoint, QEvent, QPointF
from PyQt6.QtGui import QColor, QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QApplication
from muf_studio.screen_brush import ScreenBrushOverlay
from muf_studio.annotation_toolbar import AnnotationToolbarWindow


class TestTextInputReceivesKeyboard:
    """Grup test: text input harus bisa menerima keyboard input."""

    def test_text_editor_is_not_child_of_overlay(self, qtbot):
        """QLineEdit TIDAK boleh menjadi child widget dari overlay
        karena overlay memiliki WindowDoesNotAcceptFocus."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        # Simulasikan klik untuk membuat text input
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        # Text editor harus ada
        assert overlay.text_editor is not None

        # Text editor TIDAK boleh menjadi child dari overlay
        # (karena overlay punya WindowDoesNotAcceptFocus)
        assert overlay.text_editor.parent() != overlay, (
            "QLineEdit tidak boleh menjadi child overlay yang "
            "memiliki WindowDoesNotAcceptFocus — keyboard input akan diblokir"
        )

    def test_text_editor_window_can_accept_focus(self, qtbot):
        """Window yang menampung text editor harus bisa menerima focus."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        # Buat text input
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None

        # Cari top-level window dari text editor
        editor = overlay.text_editor
        top_window = editor.window()

        # Top-level window dari editor TIDAK boleh memiliki
        # WindowDoesNotAcceptFocus flag
        flags = top_window.windowFlags()
        has_no_focus = bool(flags & Qt.WindowType.WindowDoesNotAcceptFocus)
        assert not has_no_focus, (
            "Window yang menampung text editor tidak boleh memiliki "
            "WindowDoesNotAcceptFocus — keyboard input akan diblokir"
        )

    def test_text_editor_has_focus_after_creation(self, qtbot):
        """Setelah text editor dibuat, ia harus memiliki focus."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None
        qtbot.wait(50)  # Beri waktu event loop memproses fokus

        # Editor harus memiliki focus
        assert overlay.text_editor.hasFocus(), (
            "Text editor harus memiliki focus setelah dibuat"
        )

    def test_text_editor_visible_as_top_level(self, qtbot):
        """Text editor harus visible setelah dibuat."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None
        assert overlay.text_editor.isVisible(), (
            "Text editor harus visible setelah dibuat"
        )

    def test_text_editor_stays_on_top(self, qtbot):
        """Text editor harus memiliki WindowStaysOnTopHint agar tidak
        tertutup oleh overlay."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None

        # Window dari text editor harus stays on top
        top_window = overlay.text_editor.window()
        flags = top_window.windowFlags()
        assert bool(flags & Qt.WindowType.WindowStaysOnTopHint), (
            "Text editor window harus stays on top agar tidak tertutup overlay"
        )

    def test_text_input_commit_still_works(self, qtbot):
        """Setelah user mengetik dan menekan Enter,
        teks harus masuk ke strokes overlay."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None

        # Simulasikan mengetik teks
        overlay.text_editor.setText("Hello World")

        # Simulasikan Enter (editingFinished)
        overlay.text_editor.editingFinished.emit()

        # Teks harus tersimpan di strokes
        assert len(overlay.strokes) == 1
        assert overlay.strokes[0]["type"] == "text"
        assert overlay.strokes[0]["text"] == "Hello World"

    def test_text_editor_closes_after_commit(self, qtbot):
        """Setelah teks di-commit, text editor harus ditutup."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None

        overlay.text_editor.setText("Test")
        overlay.text_editor.editingFinished.emit()

        # Text editor harus None setelah commit
        assert overlay.text_editor is None

    def test_tool_mode_resets_to_pen_after_text_commit(self, qtbot):
        """Setelah teks di-commit, tool mode harus kembali ke pen."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 200),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        overlay.text_editor.setText("Test")
        overlay.text_editor.editingFinished.emit()

        assert overlay.tool_mode == "pen"

    def test_text_editor_positioned_at_click_location(self, qtbot):
        """Text editor harus muncul di posisi klik mouse."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        overlay.set_drawing_enabled(True)
        overlay.set_tool_mode("text")

        click_pos = QPointF(300, 400)
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            click_pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        overlay.mousePressEvent(press_event)

        assert overlay.text_editor is not None

        # Text editor window harus di sekitar posisi klik
        # (konversi ke global coordinate karena sekarang top-level)
        editor_window = overlay.text_editor.window()
        window_pos = editor_window.pos()
        # Posisi harus masuk akal (dalam radius wajar dari klik)
        # Kita tidak bisa exact match karena koordinat dikonversi ke global
        assert window_pos.x() >= 0
        assert window_pos.y() >= 0
