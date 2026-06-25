import pytest
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from muf_studio.screen_brush import ScreenBrushOverlay

def test_screen_brush_initialization(qtbot):
    """Menguji inisialisasi ScreenBrushOverlay dengan flags dan attributes yang benar."""
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    # Periksa Window Flags
    flags = overlay.windowFlags()
    assert bool(flags & Qt.WindowType.FramelessWindowHint)
    assert bool(flags & Qt.WindowType.WindowStaysOnTopHint)
    assert bool(flags & Qt.WindowType.Tool)
    
    # Periksa attribute transparansi dan default click-through
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is True
    
    # Periksa default pen
    assert overlay.current_color == QColor("#ff007f") # Default neon pink/red
    assert overlay.current_width == 4

def test_screen_brush_toggle_drawing(qtbot):
    """Menguji toggle status menggambar pada overlay."""
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    # Aktifkan mode menggambar (WA_TransparentForMouseEvents harus bernilai False agar bisa menangkap klik mouse)
    overlay.set_drawing_enabled(True)
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is False
    
    # Matikan mode menggambar
    overlay.set_drawing_enabled(False)
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is True

def test_screen_brush_stroke_management(qtbot):
    """Menguji penambahan stroke, fungsi undo, dan clear."""
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    # Tambahkan stroke kosong
    assert len(overlay.strokes) == 0
    
    # Simulasikan gerakan menggambar satu coretan
    overlay.set_drawing_enabled(True)
    
    # Mulai stroke baru (mouse press)
    overlay.start_stroke(QPoint(100, 100))
    assert len(overlay.strokes) == 1
    
    # Tambah titik pada stroke (mouse move)
    overlay.add_point_to_stroke(QPoint(110, 110))
    overlay.add_point_to_stroke(QPoint(120, 120))
    
    # Verifikasi stroke aktif berisi titik-titik tersebut
    assert len(overlay.strokes[0]["points"]) == 3
    
    # Tambahkan coretan kedua
    overlay.start_stroke(QPoint(200, 200))
    overlay.add_point_to_stroke(QPoint(210, 210))
    assert len(overlay.strokes) == 2
    
    # Uji Undo
    overlay.undo()
    assert len(overlay.strokes) == 1
    
    # Uji Clear All
    overlay.clear_all()
    assert len(overlay.strokes) == 0

def test_screen_brush_pen_settings(qtbot):
    """Menguji pengaturan warna dan ukuran pen."""
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    # Ubah warna pen
    overlay.set_pen_color(QColor("#00ff87"))
    assert overlay.current_color == QColor("#00ff87")
    
    # Ubah ketebalan pen
    overlay.set_pen_width(8)
    assert overlay.current_width == 8
