from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QSlider, QCheckBox, QComboBox, QPushButton, QGroupBox
)
from PyQt6.QtGui import QFont, QIcon

class ControlPanelWindow(QWidget):
    """
    Window panel kontrol utama untuk mengatur tampilan dan parameter
    dari Floating Webcam Widget secara terpisah.
    """
    # Sinyal kustom untuk komunikasi decoupled (SOLID)
    opacity_changed = pyqtSignal(float)
    size_changed = pyqtSignal(int)
    mirror_toggled = pyqtSignal(bool)
    pause_toggled = pyqtSignal()
    source_changed = pyqtSignal(str, int)  # (source_type, camera_index)
    visibility_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Atur Properti Window
        self.setWindowTitle("Webcam Control Panel")
        self.setMinimumSize(320, 420)
        self.resize(350, 460)
        
        # 2. State Internal
        self._is_visible_state = True
        self._is_paused_state = False
        
        # 3. Inisialisasi UI
        self.setup_ui()
        self.apply_stylesheet()
        self.connect_signals()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Judul Panel ---
        title_label = QLabel("Floating Webcam Studio")
        title_label.setObjectName("TitleLabel")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("Control Panel")
        subtitle_label.setObjectName("SubtitleLabel")
        main_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # --- Group Box 1: Pengaturan Window Floating ---
        window_group = QGroupBox("Floating Window Settings")
        window_layout = QGridLayout(window_group)
        window_layout.setSpacing(12)
        window_layout.setContentsMargins(15, 20, 15, 15)
        
        # Opacity Slider
        window_layout.addWidget(QLabel("Opacity:"), 0, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100) # 10% - 100%
        self.opacity_slider.setValue(100)
        window_layout.addWidget(self.opacity_slider, 0, 1)
        
        self.opacity_val_label = QLabel("100%")
        self.opacity_val_label.setObjectName("ValueLabel")
        self.opacity_val_label.setMinimumWidth(35)
        window_layout.addWidget(self.opacity_val_label, 0, 2)
        
        # Size Slider
        window_layout.addWidget(QLabel("Size:"), 1, 0)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(120, 600)
        self.size_slider.setValue(250)
        window_layout.addWidget(self.size_slider, 1, 1)
        
        self.size_val_label = QLabel("250px")
        self.size_val_label.setObjectName("ValueLabel")
        self.size_val_label.setMinimumWidth(35)
        window_layout.addWidget(self.size_val_label, 1, 2)
        
        # Mirror Mode Checkbox
        self.mirror_checkbox = QCheckBox("Mirror Mode (Horizontal Flip)")
        self.mirror_checkbox.setChecked(True)
        window_layout.addWidget(self.mirror_checkbox, 2, 0, 1, 3)
        
        main_layout.addWidget(window_group)
        
        # --- Group Box 2: Pengaturan Kamera ---
        camera_group = QGroupBox("Camera Feed Settings")
        camera_layout = QVBoxLayout(camera_group)
        camera_layout.setSpacing(12)
        camera_layout.setContentsMargins(15, 20, 15, 15)
        
        # Combo Box Source Kamera
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Camera Source:"))
        self.source_combo = QComboBox()
        self.source_combo.addItem("Webcam (Device 0)", ("webcam", 0))
        self.source_combo.addItem("Webcam (Device 1)", ("webcam", 1))
        self.source_combo.addItem("Mock Camera (Animation)", ("mock", 0))
        combo_layout.addWidget(self.source_combo)
        camera_layout.addLayout(combo_layout)
        
        # Tombol Pause/Resume
        self.pause_button = QPushButton("⏸ Pause Feed")
        self.pause_button.setObjectName("PauseButton")
        camera_layout.addWidget(self.pause_button)
        
        main_layout.addWidget(camera_group)
        
        # --- Tombol Aksi Utama ---
        self.visibility_button = QPushButton("👁 Hide Floating Window")
        self.visibility_button.setObjectName("VisibilityButton")
        main_layout.addWidget(self.visibility_button)
        
        main_layout.addStretch()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f15;
                color: #e2e8f0;
                font-family: 'Outfit', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            #TitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #00f2fe;
                margin-bottom: -4px;
            }
            #SubtitleLabel {
                font-size: 12px;
                color: #718096;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 8px;
            }
            QGroupBox {
                border: 1px solid #232330;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                color: #a0aec0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 4px;
            }
            #ValueLabel {
                color: #00f2fe;
                font-weight: bold;
                alignment: right;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #232330;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #00f2fe;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 14px;
                height: 14px;
                margin-top: -5px;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #00f2fe;
                border: 1px solid #ffffff;
            }
            QCheckBox {
                spacing: 8px;
                color: #cbd5e0;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #232330;
                border-radius: 4px;
                background-color: #1a1a24;
            }
            QCheckBox::indicator:checked {
                background-color: #00f2fe;
                border: 1px solid #00f2fe;
                image: url(no-image); /* Just plain color check */
            }
            QComboBox {
                border: 1px solid #232330;
                border-radius: 6px;
                padding: 5px 10px;
                background-color: #1a1a24;
                color: #e2e8f0;
                min-width: 150px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
            }
            QPushButton {
                background-color: #1a1a24;
                color: #e2e8f0;
                border: 1px solid #232330;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #232330;
                border-color: #00f2fe;
            }
            QPushButton:pressed {
                background-color: #0d0d14;
            }
            #VisibilityButton {
                background-color: #1a1a24;
                color: #00f2fe;
                border: 1px solid #00f2fe;
            }
            #VisibilityButton:hover {
                background-color: #00f2fe;
                color: #0f0f15;
            }
            #PauseButton:checked, #PauseButton[active="true"] {
                color: #00ff87;
                border-color: #00ff87;
            }
        """)

    def connect_signals(self):
        # Hubungkan event internal ke emisi sinyal kustom
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        self.size_slider.valueChanged.connect(self._on_size_slider_changed)
        self.mirror_checkbox.toggled.connect(self.mirror_toggled.emit)
        
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.visibility_button.clicked.connect(self._on_visibility_clicked)

    # --- Handlers Internal ---
    
    def _on_opacity_slider_changed(self, value):
        self.opacity_val_label.setText(f"{value}%")
        self.opacity_changed.emit(value / 100.0)

    def _on_size_slider_changed(self, value):
        self.size_val_label.setText(f"{value}px")
        self.size_changed.emit(value)

    def _on_source_changed(self, index):
        data = self.source_combo.itemData(index)
        if data:
            source_type, cam_idx = data
            self.source_changed.emit(source_type, cam_idx)

    def _on_pause_clicked(self):
        # Emisi sinyal kustom
        self.pause_toggled.emit()

    def _on_visibility_clicked(self):
        # Balik status visibilitas
        self._is_visible_state = not self._is_visible_state
        self.set_visibility_state(self._is_visible_state)
        self.visibility_toggled.emit(self._is_visible_state)

    # --- Sync Setters (Dipanggil untuk menyelaraskan status dari luar secara bi-directional) ---
    
    def set_size_value(self, value):
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(value)
        self.size_val_label.setText(f"{value}px")
        self.size_slider.blockSignals(False)

    def set_opacity_value(self, value_float):
        value_int = int(value_float * 100)
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(value_int)
        self.opacity_val_label.setText(f"{value_int}%")
        self.opacity_slider.blockSignals(False)

    def set_mirror_checked(self, checked):
        self.mirror_checkbox.blockSignals(True)
        self.mirror_checkbox.setChecked(checked)
        self.mirror_checkbox.blockSignals(False)

    def set_paused_state(self, is_paused):
        self._is_paused_state = is_paused
        if is_paused:
            self.pause_button.setText("▶ Resume Feed")
            self.pause_button.setProperty("active", "true")
        else:
            self.pause_button.setText("⏸ Pause Feed")
            self.pause_button.setProperty("active", "false")
        self.pause_button.style().unpolish(self.pause_button)
        self.pause_button.style().polish(self.pause_button)

    def set_visibility_state(self, is_visible):
        self._is_visible_state = is_visible
        if is_visible:
            self.visibility_button.setText("👁 Hide Floating Window")
        else:
            self.visibility_button.setText("👁 Show Floating Window")
