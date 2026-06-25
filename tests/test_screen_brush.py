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
    # Serta WindowTransparentForInput harus bernilai False agar input mouse ditangkap
    overlay.set_drawing_enabled(True)
    qtbot.wait(100)
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is False
    assert not bool(overlay.windowFlags() & Qt.WindowType.WindowTransparentForInput)
    
    # Matikan mode menggambar (TransparentForMouseEvents & WindowTransparentForInput harus bernilai True)
    overlay.set_drawing_enabled(False)
    qtbot.wait(100)
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is True
    assert bool(overlay.windowFlags() & Qt.WindowType.WindowTransparentForInput)

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

def test_screen_brush_tool_mode(qtbot):
    """Menguji pengaturan mode tool (pen/text)."""
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    # Default tool mode harus "pen"
    assert getattr(overlay, "tool_mode", "pen") == "pen"
    
    # Set ke "text"
    overlay.set_tool_mode("text")
    assert overlay.tool_mode == "text"
    
    # Set kembali ke "pen"
    overlay.set_tool_mode("pen")
    assert overlay.tool_mode == "pen"

def test_screen_brush_text_annotation(qtbot):
    """Menguji pembuatan anotasi teks ketika klik mouse pada mode text."""
    from PyQt6.QtCore import QEvent
    from PyQt6.QtGui import QMouseEvent
    from PyQt6.QtCore import QPointF
    
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    overlay.set_drawing_enabled(True)
    overlay.set_tool_mode("text")
    
    # Simulasikan klik kiri mouse di koordinat (200, 200) untuk membuka text editor
    press_event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(200, 200),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    overlay.mousePressEvent(press_event)
    
    # Verifikasi bahwa widget editor (QLineEdit) terbuat secara dinamis pada overlay
    assert hasattr(overlay, "text_editor")
    assert overlay.text_editor is not None
    assert overlay.text_editor.isVisible()
    
    # Simulasikan mengetik teks dan tekan enter
    overlay.text_editor.setText("Halo Mas Mufid")
    # Pemicu selesainya penulisan teks
    overlay.text_editor.editingFinished.emit()
    
    # Setelah editingFinished, editor harus disembunyikan / tidak aktif
    assert overlay.text_editor is None or not overlay.text_editor.isVisible()
    
    # Verifikasi teks masuk dalam list strokes dengan tipe "text"
    assert len(overlay.strokes) == 1
    stroke = overlay.strokes[0]
    assert stroke.get("type") == "text"
    assert stroke.get("text") == "Halo Mas Mufid"
    assert stroke.get("point") == QPoint(200, 200)

def test_screen_brush_text_undo_clear(qtbot):
    """Menguji fungsionalitas undo dan clear pada coretan & teks."""
    overlay = ScreenBrushOverlay()
    qtbot.addWidget(overlay)
    
    overlay.set_drawing_enabled(True)
    
    # 1. Tambah coretan garis biasa
    overlay.start_stroke(QPoint(50, 50))
    overlay.add_point_to_stroke(QPoint(60, 60))
    
    # 2. Tambah anotasi teks secara langsung lewat model data
    text_stroke = {
        "type": "text",
        "text": "Tes Undo",
        "point": QPoint(100, 100),
        "color": QColor("#00f2fe"),
        "size": 18
    }
    overlay.strokes.append(text_stroke)
    
    assert len(overlay.strokes) == 2
    
    # Undo pertama: menghapus teks
    overlay.undo()
    assert len(overlay.strokes) == 1
    assert "type" not in overlay.strokes[0] or overlay.strokes[0].get("type") != "text"
    
    # Tambah teks lagi
    overlay.strokes.append(text_stroke)
    assert len(overlay.strokes) == 2
    
    # Clear all
    overlay.clear_all()
    assert len(overlay.strokes) == 0
