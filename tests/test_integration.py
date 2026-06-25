import pytest
from PyQt6.QtCore import Qt, QPoint
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
