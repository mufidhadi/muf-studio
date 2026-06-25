from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget

class ScreenBrushOverlay(QWidget):
    """
    Overlay transparan layar penuh (fullscreen) untuk menggambar
    atau membuat coretan guna menjelaskan materi di layar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Atur Properti Window Overlay Layar Penuh
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        
        # 2. Atur Transparansi Background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 3. Pengaturan Klik Tembus (Default: True, agar tidak memblokir desktop)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        # 4. Tampilkan secara fullscreen
        self.showFullScreen()
        
        # 5. State Internal Menggambar
        self.strokes = []  # List dari dict: {"points": [QPoint], "color": QColor, "width": int}
        self.current_color = QColor("#ff007f")  # Default Neon Pink/Red
        self.current_width = 4
        self._is_drawing_enabled = False
        self._is_drawing_active = False

    # --- API Kontrol (Dipanggil dari Panel Kontrol) ---

    def set_drawing_enabled(self, enabled):
        """Mengaktifkan/menonaktifkan mode menggambar (toggles click-through)."""
        self._is_drawing_enabled = enabled
        # Jika mode menggambar aktif, nonaktifkan click-through agar bisa menangkap mouse
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, not enabled)
        
        if enabled:
            # Ubah kursor menjadi crosshair untuk menandakan mode corat-coret
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            # Kembalikan kursor default
            self.unsetCursor()
            self._is_drawing_active = False
            
        self.update()

    def set_pen_color(self, color):
        """Mengatur warna pen saat ini."""
        self.current_color = color

    def set_pen_width(self, width):
        """Mengatur ketebalan pen saat ini."""
        self.current_width = width

    def start_stroke(self, point):
        """Memulai tarikan coretan baru."""
        stroke = {
            "points": [point],
            "color": self.current_color,
            "width": self.current_width
        }
        self.strokes.append(stroke)
        self.update()

    def add_point_to_stroke(self, point):
        """Menambahkan titik baru pada coretan aktif."""
        if self.strokes:
            self.strokes[-1]["points"].append(point)
            self.update()

    def undo(self):
        """Membatalkan coretan terakhir (Undo)."""
        if self.strokes:
            self.strokes.pop()
            self.update()

    def clear_all(self):
        """Menghapus semua coretan dari layar."""
        self.strokes.clear()
        self.update()

    # --- Mouse Events untuk Menggambar ---

    def mousePressEvent(self, event):
        if not self._is_drawing_enabled:
            event.ignore()
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing_active = True
            # Simpan posisi klik awal
            self.start_stroke(event.position().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if not self._is_drawing_enabled or not self._is_drawing_active:
            event.ignore()
            return
            
        if event.buttons() & Qt.MouseButton.LeftButton:
            # Tambahkan koordinat gerakan mouse ke stroke aktif
            self.add_point_to_stroke(event.position().toPoint())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing_active = False
            event.accept()

    # --- Paint Event untuk Merender Coretan ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Gambar semua coretan yang tersimpan
        for stroke in self.strokes:
            points = stroke["points"]
            color = stroke["color"]
            width = stroke["width"]
            
            if not points:
                continue
                
            # Konfigurasi Pen agar coretan terlihat halus (Round Cap & Join)
            pen = QPen(
                color, 
                width, 
                Qt.PenStyle.SolidLine, 
                Qt.PenCapStyle.RoundLine, 
                Qt.PenJoinStyle.RoundJoin
            )
            painter.setPen(pen)
            
            if len(points) == 1:
                # Jika hanya 1 titik, gambar titik/lingkaran kecil
                painter.drawPoint(points[0])
            else:
                # Hubungkan titik-titik membentuk garis kontinu yang halus
                for i in range(len(points) - 1):
                    painter.drawLine(points[i], points[i+1])
