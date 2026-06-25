from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QButtonGroup


class AnnotationToolbarWindow(QWidget):
    """
    Floating toolbar window terpisah (top-level) untuk kontrol anotasi layar.

    PENTING: Toolbar ini BUKAN child widget dari overlay transparan.
    Di Windows, child widget di dalam window ber-attribute WA_TranslucentBackground
    sering gagal menerima mouse events karena DWM menganggap area transparan
    sebagai "tidak ada" untuk hit-testing.

    Solusi: Toolbar dibuat sebagai window top-level independen (tanpa parent)
    dengan WindowStaysOnTopHint agar selalu melayang di atas overlay.
    """

    # Sinyal untuk komunikasi ke overlay dan control panel
    close_requested = pyqtSignal()
    tool_changed = pyqtSignal(str)
    color_changed = pyqtSignal(object)  # QColor
    undo_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        # Tidak menggunakan parent agar menjadi top-level window independen
        super().__init__(None)

        self.setObjectName("AnnotationToolbar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        # Tidak menggunakan WA_TranslucentBackground pada toolbar
        # agar semua tombol bisa diklik normal di Windows

        # Guard untuk mencegah re-entrant stylesheet update
        self._updating = False

        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        """Inisialisasi seluruh komponen UI toolbar."""
        self.setStyleSheet("""
            QWidget#AnnotationToolbar {
                background-color: rgba(15, 15, 21, 240);
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

        layout = QHBoxLayout(self)
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

        self.tb_pen.clicked.connect(lambda: self._on_tool_changed("pen"))
        self.tb_text.clicked.connect(lambda: self._on_tool_changed("text"))

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
            ("White", "#ffffff"),
        ]

        self.tb_color_buttons = []
        for name, hex_code in colors:
            btn = QPushButton()
            btn.setToolTip(name)
            btn.setFixedSize(20, 20)
            btn.setProperty("color_hex", hex_code)

            is_active = hex_code == "#ff007f"
            border_style = (
                "border: 2px solid #ffffff;"
                if is_active
                else "border: 2px solid transparent;"
            )
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
            btn.clicked.connect(
                lambda checked, h=hex_code, b=btn: self._on_color_clicked(h, b)
            )
            self.tb_color_buttons.append(btn)
            layout.addWidget(btn)

        # Pemisah
        sep3 = QLabel("|")
        sep3.setStyleSheet("color: #232330;")
        layout.addWidget(sep3)

        # Tombol Undo & Clear
        self.tb_undo = QPushButton("↩️ Undo")
        self.tb_undo.clicked.connect(self.undo_requested.emit)
        layout.addWidget(self.tb_undo)

        self.tb_clear = QPushButton("🗑️ Clear")
        self.tb_clear.clicked.connect(self.clear_requested.emit)
        layout.addWidget(self.tb_clear)

        # Pemisah
        sep4 = QLabel("|")
        sep4.setStyleSheet("color: #232330;")
        layout.addWidget(sep4)

        # Tombol Stop/Close
        self.tb_close = QPushButton("❌ Close")
        self.tb_close.setObjectName("CloseButton")
        self.tb_close.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.tb_close)

    def _on_tool_changed(self, mode):
        """Handler internal saat tombol tool berubah."""
        self.tool_changed.emit(mode)
        # Pastikan toolbar tetap di depan dan menerima input
        self.raise_()
        self.activateWindow()

    def _on_color_clicked(self, hex_code, clicked_button):
        """Handler internal saat tombol warna diklik."""
        self._updating = True
        color = QColor(hex_code)

        # Update visual style tombol warna aktif
        for btn in self.tb_color_buttons:
            h = btn.property("color_hex")
            is_active = btn == clicked_button
            border_style = (
                "border: 2px solid #ffffff;"
                if is_active
                else "border: 2px solid transparent;"
            )
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
        self._updating = False

        # Pastikan toolbar tetap di depan dan menerima input
        self.raise_()
        self.activateWindow()

    # --- API untuk sinkronisasi dari luar ---

    def set_tool_mode(self, mode):
        """Sinkronkan status tombol tool dari luar (tanpa emit sinyal)."""
        self.tb_pen.blockSignals(True)
        self.tb_text.blockSignals(True)
        if mode == "pen":
            self.tb_pen.setChecked(True)
        else:
            self.tb_text.setChecked(True)
        self.tb_pen.blockSignals(False)
        self.tb_text.blockSignals(False)

    def set_active_color(self, color):
        """Sinkronkan warna aktif dari luar (tanpa emit sinyal).
        Skip jika toolbar sedang memproses klik sendiri (mencegah double update)."""
        if self._updating:
            return
        hex_code = color.name()
        for btn in self.tb_color_buttons:
            h = btn.property("color_hex")
            is_active = h.lower() == hex_code.lower()
            border_style = (
                "border: 2px solid #ffffff;"
                if is_active
                else "border: 2px solid transparent;"
            )
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

    def position_on_screen(self, screen_geometry):
        """Posisikan toolbar di bagian tengah-atas layar yang diberikan."""
        self.adjustSize()
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + 20
        self.move(x, y)
