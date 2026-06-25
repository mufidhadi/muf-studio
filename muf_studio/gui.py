from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QPen, QImage, QAction, QActionGroup
from PyQt6.QtWidgets import QWidget, QMenu, QApplication

class FloatingWebcamWidget(QWidget):
    """
    Widget utama GUI untuk menampilkan video webcam di window persegi,
    mengambang (always on top), borderless, dan bisa digeser/di-resize.
    """
    # Sinyal kustom ketika ukuran window persegi berubah (untuk sinkronisasi control panel)
    resized = pyqtSignal(int)
    # Sinyal kustom ketika status pause webcam berubah
    pause_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Atur Window Flags agar borderless dan selalu di atas
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow  # Menghindari muncul di taskbar
        )
        
        # 2. Atur Transparansi Background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 3. Parameter Ukuran & State
        self.setMinimumSize(120, 120)
        self.setMaximumSize(600, 600)
        self.resize(250, 250)  # Ukuran default persegi
        
        self._mirror_mode = True
        self._paused = False
        self.current_frame = None
        self.drag_position = QPoint()
        
        # Mouse Tracking & Resize Configuration
        self.setMouseTracking(True)
        self.is_resizing_mode = False
        self.resize_margin = 16
        
        # 4. Callback untuk switch source kamera
        self.on_camera_source_changed = None
        
        # 5. Styling Context Menu agar bernuansa dark premium
        self.menu_style = """
            QMenu {
                background-color: #1a1a24;
                color: #e2e8f0;
                border: 1px solid #2d2d3d;
                border-radius: 8px;
                font-family: 'Outfit', 'Segoe UI', sans-serif;
                font-size: 13px;
                padding: 6px 0px;
            }
            QMenu::item {
                padding: 6px 22px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #00f2fe;
                color: #0d0d14;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2d2d3d;
                margin: 6px 12px;
            }
        """

    def is_mirror_mode(self):
        return self._mirror_mode

    def set_mirror_mode(self, enabled):
        self._mirror_mode = enabled
        self.update()

    def is_paused(self):
        return self._paused

    def toggle_pause(self):
        self._paused = not self._paused
        self.pause_changed.emit(self._paused)
        self.update()

    def set_window_opacity(self, opacity):
        self.setWindowOpacity(opacity)

    def update_frame(self, qimage):
        """Slot untuk menerima frame baru dari thread kamera."""
        if not self._paused:
            self.current_frame = qimage
            self.update()

    # --- Event Handlers ---
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Buat path persegi membulat dengan radius 24px
        path = QPainterPath()
        path.addRoundedRect(self.rect().toRectF(), 24.0, 24.0)
        
        # Kliping agar frame mengikuti bentuk rounded rect
        painter.setClipPath(path)
        
        if self.current_frame and not self.current_frame.isNull():
            # Terapkan mode mirror (balik horizontal)
            frame_to_draw = self.current_frame
            if self._mirror_mode:
                frame_to_draw = self.current_frame.mirrored(True, False)
                
            # Gambar frame video
            painter.drawImage(self.rect(), frame_to_draw)
        else:
            # Placeholder jika tidak ada frame
            painter.setBrush(QColor("#13131a"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(self.rect())
            
            # Garis hiasan/animasi pemuatan
            painter.setPen(QColor("#2d2d3d"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Loading feed...")
            
        # Nonaktifkan clipping untuk menggambar border luar agar halus
        painter.setClipping(False)
        
        # Menggambar Border Tipis (Putih dengan opacity)
        border_pen = QPen(QColor(255, 255, 255, 200), 2)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1).toRectF(), 24.0, 24.0)
        
        # Menggambar visual indicator (resize grip) diagonal di pojok kanan bawah
        grip_pen = QPen(QColor(255, 255, 255, 120), 1.5)
        painter.setPen(grip_pen)
        w, h = self.width(), self.height()
        painter.drawLine(w - 14, h - 6, w - 6, h - 14)
        painter.drawLine(w - 10, h - 6, w - 6, h - 10)
        painter.drawLine(w - 6, h - 6, w - 6, h - 6)

    # --- Mouse Events untuk Draggable & Resizable ---
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            margin = self.resize_margin
            # Cek apakah klik berada di pojok kanan bawah (resize zone)
            if pos.x() >= self.width() - margin and pos.y() >= self.height() - margin:
                self.is_resizing_mode = True
            else:
                self.is_resizing_mode = False
                # Simpan posisi offset relatif terhadap pojok kiri atas window untuk menyeret
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        margin = self.resize_margin
        
        # Hover check untuk mengubah cursor shape ketika berada di resize zone
        if not event.buttons():
            if pos.x() >= self.width() - margin and pos.y() >= self.height() - margin:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
            
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.is_resizing_mode:
                # Enforce square aspect ratio by taking the maximum of x and y
                new_size = max(pos.x(), pos.y())
                # Bound size
                new_size = max(self.minimumWidth(), min(self.maximumWidth(), new_size))
                self.resize(new_size, new_size)
            else:
                # Pindahkan window berdasarkan gerakan mouse global
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_resizing_mode = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        event.accept()

    # --- Mouse Wheel Event untuk Resize (Scalable) ---
    
    def wheelEvent(self, event):
        # Ambil delta scroll mouse (biasanya +/- 120 per notch)
        delta = event.angleDelta().y()
        step = 20 if delta > 0 else -20
        
        # Ambil posisi pusat window saat ini agar resize tetap berpusat (centered)
        old_center = self.geometry().center()
        
        # Hitung lebar baru persegi
        new_width = max(self.minimumWidth(), min(self.maximumWidth(), self.width() + step))
        self.resize(new_width, new_width)
        
        # Posisikan kembali agar titik pusat tetap sama
        new_geom = self.geometry()
        new_geom.moveCenter(old_center)
        self.setGeometry(new_geom)
        
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit(event.size().width())

    # --- Double Click untuk Pause/Resume ---
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_pause()
            event.accept()

    # --- Klik Kanan untuk Context Menu ---
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(self.menu_style)
        
        # Action: Pause / Resume
        pause_text = "▶ Resume Feed" if self._paused else "⏸ Pause Feed"
        action_pause = QAction(pause_text, self)
        action_pause.triggered.connect(self.toggle_pause)
        menu.addAction(action_pause)
        
        # Action: Mirror Mode
        action_mirror = QAction("↔ Mirror Mode", self)
        action_mirror.setCheckable(True)
        action_mirror.setChecked(self._mirror_mode)
        action_mirror.triggered.connect(lambda checked: self.set_mirror_mode(checked))
        menu.addAction(action_mirror)
        
        menu.addSeparator()
        
        # Sub-Menu: Opacity (Window Transparency)
        menu_opacity = QMenu("👁 Opacity", menu)
        menu_opacity.setStyleSheet(self.menu_style)
        
        opacity_group = QActionGroup(self)
        opacities = [("100%", 1.0), ("85%", 0.85), ("70%", 0.7), ("50%", 0.5)]
        
        current_opacity = self.windowOpacity()
        for label, val in opacities:
            act = QAction(label, self)
            act.setCheckable(True)
            act.setChecked(abs(current_opacity - val) < 0.05)
            # Karena lambda menangkap scope variabel, val=val digunakan agar nilainya diikat saat iterasi
            act.triggered.connect(lambda checked, v=val: self.set_window_opacity(v))
            opacity_group.addAction(act)
            menu_opacity.addAction(act)
            
        menu.addMenu(menu_opacity)
        
        # Sub-Menu: Input Source (Camera vs Mock)
        if self.on_camera_source_changed:
            menu_source = QMenu("📷 Input Source", menu)
            menu_source.setStyleSheet(self.menu_style)
            
            source_group = QActionGroup(self)
            
            # Action: Kamera 0
            act_cam0 = QAction("Webcam (Device 0)", self)
            act_cam0.setCheckable(True)
            # Default kamera aktif (jika callback dipanggil untuk query, 
            # untuk kesederhanaan kita buat callback saja untuk handle)
            act_cam0.triggered.connect(lambda: self.on_camera_source_changed("webcam", 0))
            source_group.addAction(act_cam0)
            menu_source.addAction(act_cam0)
            
            # Action: Kamera 1
            act_cam1 = QAction("Webcam (Device 1)", self)
            act_cam1.setCheckable(True)
            act_cam1.triggered.connect(lambda: self.on_camera_source_changed("webcam", 1))
            source_group.addAction(act_cam1)
            menu_source.addAction(act_cam1)
            
            # Action: Mock Camera
            act_mock = QAction("Mock Camera (Animasi)", self)
            act_mock.setCheckable(True)
            act_mock.triggered.connect(lambda: self.on_camera_source_changed("mock", 0))
            source_group.addAction(act_mock)
            menu_source.addAction(act_mock)
            
            menu.addMenu(menu_source)
            
        menu.addSeparator()
        
        # Action: Exit
        action_exit = QAction("❌ Exit App", self)
        action_exit.triggered.connect(QApplication.instance().quit)
        menu.addAction(action_exit)
        
        menu.exec(event.globalPos())
