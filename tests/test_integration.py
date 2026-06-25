import pytest
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from muf_studio.gui import FloatingWebcamWidget
from muf_studio.control_panel import ControlPanelWindow

def test_integration_bidirectional_sync(qtbot):
    """Menguji koordinasi dua arah antara ControlPanelWindow dan FloatingWebcamWidget."""
    widget = FloatingWebcamWidget()
    panel = ControlPanelWindow()
    
    qtbot.addWidget(widget)
    qtbot.addWidget(panel)
    
    widget.show()
    panel.show()
    
    # 1. Hubungkan sinyal dari Panel Kontrol ke Widget (Arah A: Control -> Widget)
    panel.opacity_changed.connect(widget.set_window_opacity)
    panel.size_changed.connect(lambda s: widget.resize(s, s))
    panel.mirror_toggled.connect(widget.set_mirror_mode)
    panel.visibility_toggled.connect(widget.setVisible)
    
    # 2. Hubungkan sinyal dari Widget ke Panel Kontrol (Arah B: Widget -> Control)
    # Kita bisa meniru callback resize pada widget (atau menghubungkannya di coordinator/main.py)
    # Untuk test ini, kita buat callback resizeEvent buatan atau ikuti pola sinkronisasi
    # Mari kita uji Arah A terlebih dahulu:
    
    # Opacity
    panel.opacity_slider.setValue(75)
    assert widget.windowOpacity() == pytest.approx(0.75, abs=0.01)
    
    # Size
    panel.size_slider.setValue(320)
    assert widget.width() == 320
    assert widget.height() == 320
    
    # Mirror Mode
    assert widget.is_mirror_mode() is True
    panel.mirror_checkbox.click()
    assert widget.is_mirror_mode() is False
    
    # Visibility
    assert widget.isVisible() is True
    panel.visibility_button.click()
    assert widget.isVisible() is False
    
    # 3. Uji Arah B: Ketika Widget di-resize secara manual, Panel Kontrol ter-update
    # Hubungkan sinyal resized milik widget ke setter milik panel
    widget.resized.connect(panel.set_size_value)
    
    # Simulasikan resize manual pada widget (misalnya 400x400)
    from PyQt6.QtGui import QResizeEvent
    from PyQt6.QtCore import QSize
    
    # Secara manual memicu resizeEvent untuk memintas keterbatasan window manager OS di testing headless
    widget.resizeEvent(QResizeEvent(QSize(400, 400), QSize(320, 320)))
    qtbot.wait(100)
    
    # Periksa apakah slider pada panel kontrol telah tersinkronisasi
    assert panel.size_slider.value() == 400

def test_integration_screen_brush(qtbot):
    """Menguji koordinasi antara ControlPanelWindow dan ScreenBrushOverlay."""
    from muf_studio.screen_brush import ScreenBrushOverlay
    
    panel = ControlPanelWindow()
    overlay = ScreenBrushOverlay()
    
    qtbot.addWidget(panel)
    qtbot.addWidget(overlay)
    
    # Hubungkan sinyal dari panel kontrol ke overlay
    panel.brush_mode_toggled.connect(overlay.set_drawing_enabled)
    panel.brush_width_changed.connect(overlay.set_pen_width)
    panel.brush_color_changed.connect(overlay.set_pen_color)
    panel.brush_undo_requested.connect(overlay.undo)
    panel.brush_clear_requested.connect(overlay.clear_all)
    
    # 1. Test Mode Coretan (Brush Mode)
    assert overlay._is_drawing_enabled is False
    assert overlay.isVisible() is False
    panel.brush_toggle_button.click()
    assert overlay._is_drawing_enabled is True
    assert overlay.isVisible() is True
    
    # 2. Test Brush Width
    panel.brush_width_slider.setValue(10)
    assert overlay.current_width == 10
    
    # 3. Test Brush Color
    # Simulasikan klik tombol warna Neon Cyan (#00f2fe) pada panel
    # Tombol indeks ke-1 adalah Neon Cyan
    panel.brush_color_buttons[1].click()
    assert overlay.current_color == QColor("#00f2fe")
    
    # 4. Test Undo & Clear
    # Tambahkan stroke buatan ke overlay
    overlay.start_stroke(QPoint(50, 50))
    assert len(overlay.strokes) == 1
    
    # Klik undo dari panel
    panel.brush_undo_button.click()
    assert len(overlay.strokes) == 0
    
    # Tambahkan stroke lagi
    overlay.start_stroke(QPoint(50, 50))
    assert len(overlay.strokes) == 1
    
    # Klik clear dari panel
    panel.brush_clear_button.click()
    assert len(overlay.strokes) == 0

    # Hubungkan sinyal tool changed
    panel.brush_tool_changed.connect(overlay.set_tool_mode)
    
    # 5. Test Tool Switching (Pen -> Text)
    assert overlay.tool_mode == "pen"
    panel.brush_text_tool_button.click()
    assert overlay.tool_mode == "text"
    
    panel.brush_pen_tool_button.click()
    assert overlay.tool_mode == "pen"

def test_integration_brush_bidirectional_sync(qtbot):
    """Menguji sinkronisasi dua arah antara ControlPanelWindow dan ScreenBrushOverlay."""
    from muf_studio.screen_brush import ScreenBrushOverlay
    from PyQt6.QtWidgets import QPushButton
    
    panel = ControlPanelWindow()
    overlay = ScreenBrushOverlay()
    
    qtbot.addWidget(panel)
    qtbot.addWidget(overlay)
    
    # Hubungkan sinyal dua arah (seperti di main.py)
    # Arah A: Panel Kontrol -> Overlay
    panel.brush_mode_toggled.connect(overlay.set_drawing_enabled)
    panel.brush_width_changed.connect(overlay.set_pen_width)
    panel.brush_color_changed.connect(overlay.set_pen_color)
    panel.brush_tool_changed.connect(overlay.set_tool_mode)
    
    # Arah B: Overlay -> Panel Kontrol
    overlay.drawing_toggled.connect(panel.set_brush_enabled)
    overlay.tool_changed.connect(panel.set_brush_tool)
    overlay.color_changed.connect(panel.set_brush_color)
    overlay.width_changed.connect(panel.set_brush_width)
    
    # Aktifkan drawing mode dari panel
    panel.brush_toggle_button.click()
    assert overlay.isVisible() is True
    assert overlay.toolbar.isVisible() is True
    
    # Simulasikan klik tombol Text di overlay toolbar
    text_btn = None
    for child in overlay.toolbar.findChildren(QPushButton):
        if "Text" in child.text() or "🔤" in child.text():
            text_btn = child
            break
    assert text_btn is not None
    qtbot.mouseClick(text_btn, Qt.MouseButton.LeftButton)
    
    # Verifikasi tool pada overlay dan panel berubah menjadi text
    assert overlay.tool_mode == "text"
    assert panel.brush_text_tool_button.isChecked() is True
    
    # Simulasikan klik tombol Close di overlay toolbar
    close_btn = None
    for child in overlay.toolbar.findChildren(QPushButton):
        if "Close" in child.text() or "❌" in child.text():
            close_btn = child
            break
    assert close_btn is not None
    qtbot.mouseClick(close_btn, Qt.MouseButton.LeftButton)
    
    # Verifikasi drawing mode nonaktif di overlay dan panel
    assert overlay._is_drawing_enabled is False
    assert panel.brush_toggle_button.isChecked() is False


