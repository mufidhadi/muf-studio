import pytest
from PyQt6.QtCore import Qt, QPoint
from muf_studio.gui import FloatingWebcamWidget
from muf_studio.camera import MockCameraService

def test_gui_initialization(qtbot):
    """Menguji inisialisasi FloatingWebcamWidget dengan WindowFlags dan Attributes yang benar."""
    widget = FloatingWebcamWidget()
    qtbot.addWidget(widget)
    
    # Memeriksa Window Flags
    flags = widget.windowFlags()
    assert bool(flags & Qt.WindowType.FramelessWindowHint)
    assert bool(flags & Qt.WindowType.WindowStaysOnTopHint)
    
    # Memeriksa attribute transparansi
    assert widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    # Memeriksa ukuran awal default (persegi, misal 250x250)
    assert widget.width() == widget.height()

def test_gui_mirror_mode(qtbot):
    """Menguji status mirror mode di widget."""
    widget = FloatingWebcamWidget()
    qtbot.addWidget(widget)
    
    # Default mirror mode harus True untuk kenyamanan webcam
    assert widget.is_mirror_mode() is True
    
    # Toggle mirror mode
    widget.set_mirror_mode(False)
    assert widget.is_mirror_mode() is False

def test_gui_pause_resume(qtbot):
    """Menguji status pause/resume kamera di widget."""
    widget = FloatingWebcamWidget()
    qtbot.addWidget(widget)
    
    # Default pause status adalah False (aktif)
    assert widget.is_paused() is False
    
    # Toggle pause
    widget.toggle_pause()
    assert widget.is_paused() is True
    
    # Resume
    widget.toggle_pause()
    assert widget.is_paused() is False

def test_gui_opacity_change(qtbot):
    """Menguji perubahan opacity window."""
    widget = FloatingWebcamWidget()
    qtbot.addWidget(widget)
    
    # Default opacity
    assert widget.windowOpacity() == 1.0
    
    # Ubah opacity
    widget.set_window_opacity(0.8)
    assert widget.windowOpacity() == pytest.approx(0.8)

def test_gui_drag_resize(qtbot):
    """Menguji bahwa menarik pojok kanan bawah dapat memperbesar window secara persegi."""
    widget = FloatingWebcamWidget()
    widget.show()
    qtbot.addWidget(widget)
    
    initial_size = widget.width()
    
    # Simulasikan gerakan mouse ke pojok kanan bawah
    corner = widget.rect().bottomRight() - QPoint(5, 5)
    
    # Tekan mouse kiri di pojok
    qtbot.mousePress(widget, Qt.MouseButton.LeftButton, pos=corner)
    
    # Geser mouse ke posisi baru (menambah ukuran)
    new_pos = corner + QPoint(50, 50)
    qtbot.mouseMove(widget, pos=new_pos)
    
    # Lepas mouse
    qtbot.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=new_pos)
    
    # Verifikasi ukuran bertambah dan tetap berbentuk persegi
    assert widget.width() > initial_size
    assert widget.width() == widget.height()

