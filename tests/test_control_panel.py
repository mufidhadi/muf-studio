import pytest
from PyQt6.QtCore import Qt
from muf_studio.control_panel import ControlPanelWindow

def test_control_panel_initialization(qtbot):
    """Menguji inisialisasi ControlPanelWindow dengan elemen UI yang lengkap."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    # Periksa judul window
    assert panel.windowTitle() == "MufStudio Live Panel"
    
    # Periksa keberadaan komponen utama
    assert panel.opacity_slider is not None
    assert panel.size_slider is not None
    assert panel.mirror_checkbox is not None
    assert panel.source_combo is not None
    assert panel.pause_button is not None
    assert panel.visibility_button is not None

def test_control_panel_opacity_signal(qtbot):
    """Menguji emisi sinyal opacity_changed ketika slider opacity digeser."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    def on_opacity(val):
        signals.append(val)
        
    panel.opacity_changed.connect(on_opacity)
    
    # Ubah nilai slider secara programmatif (akan memicu valueChange)
    # Range slider 10-100, kita set ke 80
    panel.opacity_slider.setValue(80)
    
    assert len(signals) == 1
    assert signals[0] == pytest.approx(0.8) # Konversi ke float 0.0 - 1.0

def test_control_panel_size_signal(qtbot):
    """Menguji emisi sinyal size_changed ketika slider size digeser."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    def on_size(val):
        signals.append(val)
        
    panel.size_changed.connect(on_size)
    
    # Slider size diatur misalnya 120-600
    panel.size_slider.setValue(300)
    
    assert len(signals) == 1
    assert signals[0] == 300

def test_control_panel_mirror_signal(qtbot):
    """Menguji emisi sinyal mirror_toggled saat checkbox diklik."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    def on_mirror(checked):
        signals.append(checked)
        
    panel.mirror_toggled.connect(on_mirror)
    
    # Simulasikan klik checkbox secara programmatik untuk keandalan test
    panel.mirror_checkbox.click()
    
    # Secara default mirror aktif (True), setelah klik harus menjadi False
    assert len(signals) == 1
    assert signals[0] is False

def test_control_panel_visibility_signal(qtbot):
    """Menguji emisi sinyal visibility_toggled saat tombol hide/show diklik."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    def on_vis(visible):
        signals.append(visible)
        
    panel.visibility_toggled.connect(on_vis)
    
    # Klik tombol visibility secara programmatik
    panel.visibility_button.click()
    
    assert len(signals) == 1
    assert signals[0] is False

def test_control_panel_brush_initialization(qtbot):
    """Menguji inisialisasi elemen UI alat coretan (screen brush) pada panel kontrol."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    assert panel.brush_toggle_button is not None
    assert panel.brush_undo_button is not None
    assert panel.brush_clear_button is not None
    assert panel.brush_width_slider is not None
    assert len(panel.brush_color_buttons) > 0

def test_control_panel_brush_mode_toggled(qtbot):
    """Menguji emisi sinyal brush_mode_toggled saat tombol coretan diklik."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    panel.brush_mode_toggled.connect(signals.append)
    
    # Klik tombol toggle mode gambar
    panel.brush_toggle_button.click()
    
    # Secara default mode gambar mati (False), setelah diklik harus menjadi True
    assert len(signals) == 1
    assert signals[0] is True
    
    # Klik sekali lagi
    panel.brush_toggle_button.click()
    assert len(signals) == 2
    assert signals[1] is False

def test_control_panel_brush_width_changed(qtbot):
    """Menguji emisi sinyal brush_width_changed saat slider ketebalan pen digeser."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    panel.brush_width_changed.connect(signals.append)
    
    # Geser slider ketebalan coretan ke 8px
    panel.brush_width_slider.setValue(8)
    
    assert len(signals) == 1
    assert signals[0] == 8

def test_control_panel_brush_undo_requested(qtbot):
    """Menguji emisi sinyal brush_undo_requested saat tombol undo diklik."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    panel.brush_undo_requested.connect(lambda: signals.append(True))
    
    panel.brush_undo_button.click()
    assert len(signals) == 1

def test_control_panel_brush_clear_requested(qtbot):
    """Menguji emisi sinyal brush_clear_requested saat tombol clear diklik."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    signals = []
    panel.brush_clear_requested.connect(lambda: signals.append(True))
    
    panel.brush_clear_button.click()
    assert len(signals) == 1

def test_control_panel_brush_tool_selection(qtbot):
    """Menguji emisi sinyal brush_tool_changed saat memilih tool menggambar (Pen vs Text)."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    assert panel.brush_pen_tool_button is not None
    assert panel.brush_text_tool_button is not None
    
    signals = []
    panel.brush_tool_changed.connect(signals.append)
    
    # Klik tombol Text Tool secara programmatif
    panel.brush_text_tool_button.click()
    assert len(signals) == 1
    assert signals[0] == "text"
    
    # Klik tombol Pen Tool secara programmatif
    panel.brush_pen_tool_button.click()
    assert len(signals) == 2
    assert signals[1] == "pen"

def test_control_panel_brush_sync_setters(qtbot):
    """Menguji setter sinkronisasi dua arah untuk status brush pada panel kontrol."""
    from PyQt6.QtGui import QColor
    
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    # 1. Test set_brush_enabled
    panel.set_brush_enabled(True)
    assert panel.brush_toggle_button.isChecked() is True
    assert "Stop Drawing" in panel.brush_toggle_button.text()
    
    panel.set_brush_enabled(False)
    assert panel.brush_toggle_button.isChecked() is False
    assert "Start Drawing" in panel.brush_toggle_button.text()
    
    # 2. Test set_brush_tool
    panel.set_brush_tool("text")
    assert panel.brush_text_tool_button.isChecked() is True
    assert panel.brush_pen_tool_button.isChecked() is False
    
    panel.set_brush_tool("pen")
    assert panel.brush_pen_tool_button.isChecked() is True
    assert panel.brush_text_tool_button.isChecked() is False
    
    # 3. Test set_brush_width
    panel.set_brush_width(12)
    assert panel.brush_width_slider.value() == 12
    assert "12px" in panel.brush_width_val_label.text()
    
    # 4. Test set_brush_color
    cyan = QColor("#00f2fe")
    panel.set_brush_color(cyan)


