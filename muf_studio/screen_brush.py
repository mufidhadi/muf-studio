from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication

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
        
        # 2. Atur Transparansi Background secara eksplisit
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        
        # 3. Posisikan menutupi seluruh screen primer sejak awal
        # Menggunakan geometry manual alih-alih showFullScreen() yang eksklusif
        # agar DWM Windows tetap mengaktifkan composition/transparansi.
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # 4. Mode Menggambar nonaktif secara default pada startup (Window disembunyikan)
        self.hide()
        
        # 5. State Internal Menggambar
        self.strokes = []  # List dari dict: {"points": [QPoint], "color": QColor, "width": int}
        self.current_color = QColor("#ff007f")  # Default Neon Pink/Red
        self.current_width = 4
        self._is_drawing_enabled = False
        self._is_drawing_active = False
        self.tool_mode = "pen"  # "pen" atau "text"
        self.text_editor = None

    # --- API Kontrol (Dipanggil dari Panel Kontrol) ---

    def set_drawing_enabled(self, enabled):
        """Mengaktifkan/menonaktifkan mode menggambar (toggles visibility)."""
        self._is_drawing_enabled = enabled
        
        if enabled:
            # Posisikan menutupi seluruh screen primer sebelum ditampilkan
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)
            
            # Tampilkan overlay, bawa ke depan, dan aktifkan fokus
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Ubah kursor menjadi crosshair untuk menandakan mode corat-coret
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            # Jika ada text editor aktif, selesaikan
            if self.text_editor is not None:
                self.text_editor.editingFinished.emit()
            
            # Kembalikan kursor default
            self.unsetCursor()
            self._is_drawing_active = False
            
            # Sembunyikan overlay agar input mouse sepenuhnya kembali ke desktop
            self.hide()
            
        self.update()

    def set_tool_mode(self, mode):
        """Mengatur mode tool aktif (pen atau text)."""
        self.tool_mode = mode
        # Jika ada text editor yang sedang aktif, selesaikan
        if self.text_editor is not None:
            self.text_editor.editingFinished.emit()

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

    def create_text_input(self, pos):
        """Membuat input teks mengambang pada posisi klik."""
        self.text_editor = QLineEdit(self)
        self.text_editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        # Ukuran font sebanding dengan ketebalan pen, minimal 14px
        font_size = max(14, self.current_width * 4)
        self.text_editor.setFont(QFont("Outfit", font_size))
        
        # Style premium: semi-transparan, border tipis neon
        color_hex = self.current_color.name()
        self.text_editor.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(15, 15, 21, 0.85);
                color: {color_hex};
                border: 1px dashed {color_hex};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        
        # Posisikan editor dan fokus
        self.text_editor.move(pos)
        self.text_editor.resize(250, font_size + 16)
        
        # Hubungkan signal saat selesai menulis (tekan enter atau hilangnya fokus)
        self.text_editor.editingFinished.connect(lambda p=pos, fs=font_size: self._on_text_editing_finished(p, fs))
        self.text_editor.show()
        self.text_editor.setFocus()

    def _on_text_editing_finished(self, pos, font_size):
        if self.text_editor is None:
            return
            
        text = self.text_editor.text().strip()
        if text:
            # Simpan tipe anotasi sebagai teks
            self.strokes.append({
                "type": "text",
                "text": text,
                "point": pos,
                "color": self.current_color,
                "size": font_size
            })
            
        editor = self.text_editor
        self.text_editor = None
        editor.close()
        self.update()

    def undo(self):
        """Membatalkan coretan terakhir (Undo)."""
        if self.strokes:
            self.strokes.pop()
            self.update()

    def clear_all(self):
        """Menghapus semua coretan dari layar."""
        self.strokes.clear()
        if self.text_editor is not None:
            self.text_editor.close()
            self.text_editor = None
        self.update()

    # --- Mouse Events untuk Menggambar ---

    def mousePressEvent(self, event):
        if not self._is_drawing_enabled:
            event.ignore()
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool_mode == "pen":
                self._is_drawing_active = True
                # Simpan posisi klik awal
                self.start_stroke(event.position().toPoint())
                event.accept()
            elif self.tool_mode == "text":
                # Jika sudah ada text editor aktif, selesaikan dulu
                if self.text_editor is not None:
                    self.text_editor.editingFinished.emit()
                
                # Buat QLineEdit baru secara dinamis pada posisi klik
                pos = event.position().toPoint()
                self.create_text_input(pos)
                event.accept()

    def mouseMoveEvent(self, event):
        if not self._is_drawing_enabled or not self._is_drawing_active:
            event.ignore()
            return
            
        if self.tool_mode == "pen" and (event.buttons() & Qt.MouseButton.LeftButton):
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
        
        # Isi background dengan warna hitam super transparan (alpha = 1)
        # agar Windows OS menangkap input mouse dan tidak membiarkannya tembus klik.
        # Opacity 1/255 secara visual 100% tidak terlihat oleh mata manusia.
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
        # Gambar semua coretan yang tersimpan
        for stroke in self.strokes:
            stroke_type = stroke.get("type", "path")
            color = stroke["color"]
            
            if stroke_type == "text":
                text = stroke["text"]
                point = stroke["point"]
                size = stroke.get("size", 16)
                
                painter.setFont(QFont("Outfit", size))
                painter.setPen(color)
                painter.drawText(point, text)
            else:
                points = stroke["points"]
                width = stroke["width"]
                
                if not points:
                    continue
                    
                # Konfigurasi Pen agar coretan terlihat halus (Round Cap & Join)
                pen = QPen(
                    color, 
                    width, 
                    Qt.PenStyle.SolidLine, 
                    Qt.PenCapStyle.RoundCap, 
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
