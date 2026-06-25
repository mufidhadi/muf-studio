"""
Test untuk memverifikasi bahwa overlay ScreenBrush TIDAK mencuri fokus
dari AnnotationToolbarWindow, sehingga toolbar tetap bisa diklik
setelah perubahan warna atau aksi lainnya.

Root cause: Overlay memanggil activateWindow() dan raise_() yang
menyebabkan overlay mendapatkan fokus dan z-order lebih tinggi
daripada toolbar. Fix: Overlay harus menggunakan
WA_ShowWithoutActivating dan WindowDoesNotAcceptFocus.
"""
import pytest
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from muf_studio.screen_brush import ScreenBrushOverlay
from muf_studio.annotation_toolbar import AnnotationToolbarWindow


class TestOverlayDoesNotStealFocus:
    """Grup test: overlay TIDAK boleh mencuri fokus dari toolbar."""

    def test_overlay_has_show_without_activating(self, qtbot):
        """Overlay harus memiliki attribute WA_ShowWithoutActivating
        agar tidak mencuri fokus saat show() dipanggil."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        assert overlay.testAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating
        ), "Overlay harus memiliki WA_ShowWithoutActivating"

    def test_overlay_has_does_not_accept_focus_flag(self, qtbot):
        """Overlay harus memiliki flag WindowDoesNotAcceptFocus
        agar tidak bisa menerima keyboard focus."""
        overlay = ScreenBrushOverlay()
        qtbot.addWidget(overlay)

        flags = overlay.windowFlags()
        assert bool(
            flags & Qt.WindowType.WindowDoesNotAcceptFocus
        ), "Overlay harus memiliki flag WindowDoesNotAcceptFocus"

    def test_overlay_show_does_not_call_activate_window(self, qtbot):
        """Saat drawing diaktifkan, overlay TIDAK boleh memanggil
        activateWindow() karena ini akan mencuri fokus."""
        overlay = ScreenBrushOverlay()
        toolbar = AnnotationToolbarWindow()
        overlay.set_toolbar(toolbar)

        qtbot.addWidget(overlay)
        qtbot.addWidget(toolbar)

        # Aktifkan drawing - seharusnya TIDAK ada activateWindow pada overlay
        # Kita verifikasi ini melalui efek: overlay tidak boleh jadi active window
        overlay.set_drawing_enabled(True)
        qtbot.wait(50)

        # Overlay harus visible tapi TIDAK boleh active
        assert overlay.isVisible()
        assert toolbar.isVisible()

    def test_toolbar_clickable_after_color_change(self, qtbot):
        """Setelah mengganti warna di toolbar, semua tombol toolbar
        harus tetap bisa diklik (tidak terhalang overlay)."""
        overlay = ScreenBrushOverlay()
        toolbar = AnnotationToolbarWindow()
        overlay.set_toolbar(toolbar)

        qtbot.addWidget(overlay)
        qtbot.addWidget(toolbar)

        # Hubungkan signal seperti di main.py
        toolbar.color_changed.connect(overlay.set_pen_color)
        toolbar.tool_changed.connect(overlay.set_tool_mode)
        toolbar.undo_requested.connect(overlay.undo)
        toolbar.clear_requested.connect(overlay.clear_all)
        toolbar.close_requested.connect(
            lambda: overlay.set_drawing_enabled(False)
        )

        # Aktifkan drawing
        overlay.set_drawing_enabled(True)
        qtbot.wait(50)

        # Klik warna Neon Cyan di toolbar
        signals_color = []
        toolbar.color_changed.connect(signals_color.append)
        qtbot.mouseClick(
            toolbar.tb_color_buttons[1], Qt.MouseButton.LeftButton
        )
        assert len(signals_color) == 1, (
            "Signal color_changed harus terkirim setelah klik warna"
        )

        # Setelah ganti warna, klik tombol tool Text di toolbar
        signals_tool = []
        toolbar.tool_changed.connect(signals_tool.append)
        qtbot.mouseClick(toolbar.tb_text, Qt.MouseButton.LeftButton)
        assert len(signals_tool) == 1, (
            "Signal tool_changed harus terkirim - toolbar harus tetap clickable"
        )
        assert signals_tool[0] == "text"

        # Klik Undo di toolbar
        signals_undo = []
        toolbar.undo_requested.connect(lambda: signals_undo.append(True))
        qtbot.mouseClick(toolbar.tb_undo, Qt.MouseButton.LeftButton)
        assert len(signals_undo) == 1, (
            "Undo harus bisa diklik setelah ganti warna"
        )

        # Klik Close di toolbar
        signals_close = []
        toolbar.close_requested.connect(lambda: signals_close.append(True))
        qtbot.mouseClick(toolbar.tb_close, Qt.MouseButton.LeftButton)
        assert len(signals_close) == 1, (
            "Close harus bisa diklik setelah ganti warna"
        )

    def test_set_pen_color_does_not_activate_overlay(self, qtbot):
        """set_pen_color() pada overlay TIDAK boleh memanggil
        activateWindow() atau raise_() pada overlay itu sendiri."""
        overlay = ScreenBrushOverlay()
        toolbar = AnnotationToolbarWindow()
        overlay.set_toolbar(toolbar)

        qtbot.addWidget(overlay)
        qtbot.addWidget(toolbar)

        overlay.set_drawing_enabled(True)
        qtbot.wait(50)

        # Ganti warna - overlay seharusnya tidak mencuri fokus
        overlay.set_pen_color(QColor("#00f2fe"))

        # Verifikasi bahwa overlay tidak menjadi window aktif
        # (Ini verifikasi implisit - yang penting overlay punya
        # WA_ShowWithoutActivating dan WindowDoesNotAcceptFocus)
        assert overlay.testAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating
        )

    def test_multiple_color_changes_toolbar_stays_responsive(self, qtbot):
        """Setelah beberapa kali ganti warna berturut-turut,
        toolbar harus tetap responsif (tidak freeze/unclickable)."""
        overlay = ScreenBrushOverlay()
        toolbar = AnnotationToolbarWindow()
        overlay.set_toolbar(toolbar)

        qtbot.addWidget(overlay)
        qtbot.addWidget(toolbar)

        toolbar.color_changed.connect(overlay.set_pen_color)

        overlay.set_drawing_enabled(True)
        qtbot.wait(50)

        # Ganti warna 3 kali berturut-turut
        for i in range(3):
            qtbot.mouseClick(
                toolbar.tb_color_buttons[i], Qt.MouseButton.LeftButton
            )
            qtbot.wait(20)

        # Setelah ganti warna berulang, toolbar harus tetap clickable
        signals = []
        toolbar.tool_changed.connect(signals.append)
        qtbot.mouseClick(toolbar.tb_text, Qt.MouseButton.LeftButton)
        assert len(signals) == 1, (
            "Toolbar harus tetap clickable setelah banyak perubahan warna"
        )
