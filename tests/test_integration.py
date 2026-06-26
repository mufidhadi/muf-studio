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
    widget.resized.connect(panel.set_size_value)
    
    from PyQt6.QtGui import QResizeEvent
    from PyQt6.QtCore import QSize
    
    widget.resizeEvent(QResizeEvent(QSize(400, 400), QSize(320, 320)))
    qtbot.wait(100)
    
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
    panel.brush_color_buttons[1].click()
    assert overlay.current_color == QColor("#00f2fe")
    
    # 4. Test Undo & Clear
    overlay.start_stroke(QPoint(50, 50))
    assert len(overlay.strokes) == 1
    
    panel.brush_undo_button.click()
    assert len(overlay.strokes) == 0
    
    overlay.start_stroke(QPoint(50, 50))
    assert len(overlay.strokes) == 1
    
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
    """Menguji sinkronisasi dua arah antara ControlPanelWindow, ScreenBrushOverlay, dan AnnotationToolbarWindow."""
    from muf_studio.screen_brush import ScreenBrushOverlay
    from muf_studio.annotation_toolbar import AnnotationToolbarWindow
    
    panel = ControlPanelWindow()
    overlay = ScreenBrushOverlay()
    toolbar = AnnotationToolbarWindow()
    overlay.set_toolbar(toolbar)
    
    qtbot.addWidget(panel)
    qtbot.addWidget(overlay)
    qtbot.addWidget(toolbar)
    
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

    # Arah C: Toolbar -> Overlay & Panel
    toolbar.close_requested.connect(lambda: overlay.set_drawing_enabled(False))
    toolbar.tool_changed.connect(overlay.set_tool_mode)
    toolbar.tool_changed.connect(panel.set_brush_tool)
    toolbar.color_changed.connect(overlay.set_pen_color)
    toolbar.color_changed.connect(panel.set_brush_color)
    toolbar.undo_requested.connect(overlay.undo)
    toolbar.clear_requested.connect(overlay.clear_all)
    
    # Aktifkan drawing mode dari panel
    panel.brush_toggle_button.click()
    assert overlay.isVisible() is True
    assert toolbar.isVisible() is True  # Toolbar terpisah juga muncul
    
    # Simulasikan klik tombol Text di TOOLBAR TERPISAH (bukan child overlay)
    qtbot.mouseClick(toolbar.tb_text, Qt.MouseButton.LeftButton)
    
    # Verifikasi tool pada overlay DAN panel berubah menjadi text
    assert overlay.tool_mode == "text"
    assert panel.brush_text_tool_button.isChecked() is True
    
    # Simulasikan klik warna dari toolbar
    qtbot.mouseClick(toolbar.tb_color_buttons[2], Qt.MouseButton.LeftButton)  # Neon Green
    assert overlay.current_color == QColor("#00ff87")
    
    # Simulasikan klik tombol Close di toolbar
    qtbot.mouseClick(toolbar.tb_close, Qt.MouseButton.LeftButton)
    
    # Verifikasi drawing mode nonaktif di overlay dan panel
    assert overlay._is_drawing_enabled is False
    assert overlay.isHidden() is True
    assert toolbar.isHidden() is True
    assert panel.brush_toggle_button.isChecked() is False

def test_integration_screen_recorder(qtbot, tmp_path):
    """Menguji koordinasi antara ControlPanelWindow dan ScreenRecorder menggunakan MockScreenRecorder."""
    from muf_studio.recorder import MockScreenRecorder
    
    panel = ControlPanelWindow()
    recorder = MockScreenRecorder()
    
    qtbot.addWidget(panel)
    
    # Simulasikan inisialisasi awal list monitor dan device audio
    monitors = recorder.get_available_monitors()
    panel.set_available_monitors(monitors)
    devices = recorder.get_available_audio_devices()
    panel.set_available_audio_devices(devices)
    
    # Hubungkan sinyal dari panel kontrol ke recorder
    def on_start_recording(monitor_idx, audio_device_idx):
        output_path = str(tmp_path / "test_recording_run.mp4")
        success = recorder.start_recording(monitor_idx, output_path, audio_device_idx)
        if success:
            panel.set_recording_state(True)
            
    def on_stop_recording():
        recorder.stop_recording()
        panel.set_recording_state(False)
        
    panel.start_recording_requested.connect(on_start_recording)
    panel.stop_recording_requested.connect(on_stop_recording)
    
    # 1. Mulai perekaman
    assert not recorder.is_recording()
    qtbot.mouseClick(panel.record_button, Qt.MouseButton.LeftButton)
    assert recorder.is_recording()
    assert panel.record_button.text() == "🛑 Stop Recording"
    
    # 2. Hentikan perekaman
    qtbot.mouseClick(panel.record_button, Qt.MouseButton.LeftButton)
    assert not recorder.is_recording()
    assert panel.record_button.text() == "⏺ Start Recording"



