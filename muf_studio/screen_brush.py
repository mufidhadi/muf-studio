from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QGuiApplication, QCursor
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication, QHBoxLayout, QPushButton, QLabel, QButtonGroup

class ScreenBrushOverlay(QWidget):
    """
    Overlay transparan layar penuh (fullscreen) untuk menggambar
    atau membuat coretan guna menjelaskan materi di layar.
    """
    drawing_toggled = pyqtSignal(bool)
    tool_changed = pyqtSignal(str)
    color_changed = pyqtSignal(object)  # QColor
    width_changed = pyqtSignal(int)
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
        
        # 6. Tambahkan Floating Toolbar
        self.setup_toolbar()

    # --- API Kontrol (Dipanggil dari Panel Kontrol) ---

    def set_drawing_enabled(self, enabled):
        """Mengaktifkan/menonaktifkan mode menggambar (toggles visibility)."""
        self._is_drawing_enabled = enabled
        
        if enabled:
            # Dapatkan monitor tempat mouse berada saat ini agar mendukung multi-monitor secara seamless
            active_screen = QGuiApplication.screenAt(QCursor.pos())
            if active_screen is None:
                active_screen = QApplication.primaryScreen()
            self.setGeometry(active_screen.geometry())
            
            # Tampilkan overlay, bawa ke depan, dan aktifkan fokus
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Ubah kursor menjadi crosshair untuk menandakan mode corat-coret
            self.setCursor(Qt.CursorShape.CrossCursor)
            
            # Tampilkan toolbar
            if hasattr(self, 'toolbar'):
                self.toolbar.show()
                self.toolbar.adjustSize()
                self.toolbar.move((self.width() - self.toolbar.width()) // 2, 20)
        else:
            # Jika ada text editor aktif, selesaikan
            if self.text_editor is not None:
                self.text_editor.editingFinished.emit()
            
            # Kembalikan kursor default
            self.unsetCursor()
            self._is_drawing_active = False
            
            # Sembunyikan toolbar
            if hasattr(self, 'toolbar'):
                self.toolbar.hide()
            
            # Sembunyikan overlay agar input mouse sepenuhnya kembali ke desktop
            self.hide()
            
        self.drawing_toggled.emit(enabled)
        self.update()

    def set_tool_mode(self, mode):
        """Mengatur mode tool aktif (pen atau text)."""
        self.tool_mode = mode
        # Jika ada text editor yang sedang aktif, selesaikan
        if self.text_editor is not None:
            self.text_editor.editingFinished.emit()
            
        # Sinkronkan status tombol di toolbar
        if hasattr(self, 'tb_pen'):
            self.tb_pen.blockSignals(True)
            self.tb_text.blockSignals(True)
            if mode == "pen":
                self.tb_pen.setChecked(True)
            else:
                self.tb_text.setChecked(True)
            self.tb_pen.blockSignals(False)
            self.tb_text.blockSignals(False)

    def set_pen_color(self, color):
        """Mengatur warna pen saat ini."""
        self.current_color = color
        
        # Sinkronkan warna aktif di toolbar
        if hasattr(self, 'tb_color_buttons'):
            hex_code = color.name()
            for btn in self.tb_color_buttons:
                h = btn.property("color_hex")
                is_active = (h.lower() == hex_code.lower())
                border_style = "border: 2px solid #ffffff;" if is_active else "border: 2px solid transparent;"
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {h};
                        border-radius: 10px;
                        {border_style}
                    }}
                    QPushButton:hover {{
                        border: 2px solid #a0aec0;
                    }}
                """)

    def set_pen_width(self, width):
        """Mengatur ketebalan pen saat ini."""
        self.current_width = width
        self.width_changed.emit(width)

    def setup_toolbar(self):
        self.toolbar = QWidget(self)
        self.toolbar.setObjectName("AnnotationToolbar")
        self.toolbar.setStyleSheet("""
            QWidget#AnnotationToolbar {
                background-color: rgba(15, 15, 21, 0.95);
                border: 1px solid #ff007f;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #1a1a24;
                color: #e2e8f0;
                border: 1px solid #232330;
                border-radius: 6px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #232330;
                border-color: #00f2fe;
            }
            QPushButton:checked {
                background-color: #ff007f;
                color: #ffffff;
                border-color: #ff007f;
            }
            QPushButton#CloseButton {
                background-color: #2d1618;
                border-color: #e53e3e;
                color: #feb2b2;
            }
            QPushButton#CloseButton:hover {
                background-color: #e53e3e;
                color: #ffffff;
            }
            QLabel {
                color: #a0aec0;
                font-weight: bold;
                font-size: 11px;
                padding: 0 4px;
            }
        """)
        
        layout = QHBoxLayout(self.toolbar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)
        
        # Label Title/Grip
        title_label = QLabel("Studio Pen ✏️")
        layout.addWidget(title_label)
        
        # Pemisah
        sep1 = QLabel("|")
        sep1.setStyleSheet("color: #232330;")
        layout.addWidget(sep1)
        
        # Button Tool: Pen & Text
        self.tb_pen = QPushButton("✏️ Pen")
        self.tb_pen.setCheckable(True)
        self.tb_pen.setChecked(True)
        
        self.tb_text = QPushButton("🔤 Text")
        self.tb_text.setCheckable(True)
        
        self.tb_tool_group = QButtonGroup(self)
        self.tb_tool_group.addButton(self.tb_pen)
        self.tb_tool_group.addButton(self.tb_text)
        self.tb_tool_group.setExclusive(True)
        
        self.tb_pen.clicked.connect(lambda: self._on_tb_tool_changed("pen"))
        self.tb_text.clicked.connect(lambda: self._on_tb_tool_changed("text"))
        
        layout.addWidget(self.tb_pen)
        layout.addWidget(self.tb_text)
        
        # Pemisah
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: #232330;")
        layout.addWidget(sep2)
        
        # Warna Pen (Circular Buttons)
        colors = [
            ("Neon Pink", "#ff007f"),
            ("Neon Cyan", "#00f2fe"),
            ("Neon Green", "#00ff87"),
            ("Neon Yellow", "#ffe259"),
            ("White", "#ffffff")
        ]
        
        self.tb_color_buttons = []
        for name, hex_code in colors:
            btn = QPushButton()
            btn.setToolTip(name)
            btn.setFixedSize(20, 20)
            btn.setProperty("color_hex", hex_code)
            
            is_active = (hex_code == "#ff007f")
            border_style = "border: 2px solid #ffffff;" if is_active else "border: 2px solid transparent;"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_code};
                    border-radius: 10px;
                    {border_style}
                }}
                QPushButton:hover {{
                    border: 2px solid #a0aec0;
                }}
            """)
            btn.clicked.connect(lambda checked, h=hex_code, b=btn: self._on_tb_color_clicked(h, b))
            self.tb_color_buttons.append(btn)
            layout.addWidget(btn)
            
        # Pemisah
        sep3 = QLabel("|")
        sep3.setStyleSheet("color: #232330;")
        layout.addWidget(sep3)
        
        # Tombol Undo & Clear
        self.tb_undo = QPushButton("↩️ Undo")
        self.tb_undo.clicked.connect(self.undo)
        layout.addWidget(self.tb_undo)
        
        self.tb_clear = QPushButton("🗑️ Clear")
        self.tb_clear.clicked.connect(self.clear_all)
        layout.addWidget(self.tb_clear)
        
        # Pemisah
        sep4 = QLabel("|")
        sep4.setStyleSheet("color: #232330;")
        layout.addWidget(sep4)
        
        # Tombol Stop/Close
        self.tb_close = QPushButton("❌ Close")
        self.tb_close.setObjectName("CloseButton")
        self.tb_close.clicked.connect(lambda: self.set_drawing_enabled(False))
        layout.addWidget(self.tb_close)
        
        self.toolbar.hide()

    def _on_tb_tool_changed(self, mode):
        self.set_tool_mode(mode)
        self.tool_changed.emit(mode)

    def _on_tb_color_clicked(self, hex_code, clicked_button):
        color = QColor(hex_code)
        self.set_pen_color(color)
        
        # Update style lingkaran aktif di toolbar
        for btn in self.tb_color_buttons:
            h = btn.property("color_hex")
            is_active = (btn == clicked_button)
            border_style = "border: 2px solid #ffffff;" if is_active else "border: 2px solid transparent;"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {h};
                    border-radius: 10px;
                    {border_style}
                }}
                QPushButton:hover {{
                    border: 2px solid #a0aec0;
                }}
            """)
            
        self.color_changed.emit(color)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'toolbar') and self.toolbar.isVisible():
            self.toolbar.adjustSize()
            self.toolbar.move((self.width() - self.toolbar.width()) // 2, 20)

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
        
        # Isi background dengan warna hitam super transparan (alpha = 5)
        # agar Windows OS menangkap input mouse dan tidak membiarkannya tembus klik.
        # Opacity 5/255 secara visual 100% tidak terlihat oleh mata manusia (sekitar 1.96%),
        # namun sangat aman terhadap pembulatan interpolasi saat DPI scaling Windows aktif.
        painter.fillRect(self.rect(), QColor(0, 0, 0, 5))
        
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
