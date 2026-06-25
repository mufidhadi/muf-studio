import pytest
from PyQt6.QtCore import Qt
from muf_studio.control_panel import ControlPanelWindow

def test_control_panel_initialization(qtbot):
    """Menguji inisialisasi ControlPanelWindow dengan elemen UI yang lengkap."""
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    # Periksa judul window
    assert panel.windowTitle() == "Webcam Control Panel"
    
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
