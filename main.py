import sys
import argparse
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from muf_studio.camera import MockCameraService, OpenCVCameraService
from muf_studio.gui import FloatingWebcamWidget
from muf_studio.control_panel import ControlPanelWindow
from muf_studio.screen_brush import ScreenBrushOverlay

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Floating Webcam GUI - Window webcam mengambang yang elegan dan minimalis."
    )
    parser.add_argument(
        "-c", "--camera",
        type=int,
        default=0,
        help="Indeks perangkat kamera webcam (default: 0)."
    )
    parser.add_argument(
        "-m", "--mock",
        action="store_true",
        help="Gunakan Mock Camera (kamera tiruan dengan animasi) saat startup."
    )
    parser.add_argument(
        "-f", "--fps",
        type=int,
        default=30,
        help="Frame rate per detik untuk pembacaan kamera (default: 30)."
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # 1. Inisialisasi Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Floating Webcam Studio")
    
    # 2. Inisialisasi Tampilan Widget, Panel Kontrol, & Brush Overlay
    widget = FloatingWebcamWidget()
    panel = ControlPanelWindow()
    brush_overlay = ScreenBrushOverlay()
    
    active_thread = None
    fps = args.fps

    # 3. Fungsi untuk melakukan switch source kamera secara dinamis
    def change_camera_source(source_type, index=0):
        nonlocal active_thread
        
        # Hentikan thread kamera yang sedang aktif jika ada
        if active_thread is not None:
            try:
                active_thread.frame_received.disconnect(widget.update_frame)
            except TypeError:
                pass # Sinyal mungkin tidak terhubung
            active_thread.stop()
            active_thread.wait()
            active_thread = None
            
        # Buat thread kamera baru berdasarkan pilihan
        if source_type == "mock":
            print("Beralih ke Mock Camera...")
            active_thread = MockCameraService(fps=fps)
            # Selaraskan combobox pada panel kontrol
            panel.source_combo.blockSignals(True)
            panel.source_combo.setCurrentIndex(2)  # Mock Camera
            panel.source_combo.blockSignals(False)
        else:
            print(f"Beralih ke Webcam Device {index}...")
            active_thread = OpenCVCameraService(camera_index=index, fps=fps)
            # Selaraskan combobox pada panel kontrol
            panel.source_combo.blockSignals(True)
            panel.source_combo.setCurrentIndex(index)  # Webcam index 0 atau 1
            panel.source_combo.blockSignals(False)
            
        # Hubungkan sinyal frame baru ke widget
        active_thread.frame_received.connect(widget.update_frame)
        active_thread.start()

    # Daftarkan callback switch camera ke widget (klik kanan menu)
    widget.on_camera_source_changed = change_camera_source

    # --- Koordinasi Sinyal Bi-directional (SOLID) ---
    
    # Arah A: Panel Kontrol -> Floating Widget
    panel.opacity_changed.connect(widget.set_window_opacity)
    panel.size_changed.connect(lambda s: widget.resize(s, s))
    panel.mirror_toggled.connect(widget.set_mirror_mode)
    panel.pause_toggled.connect(widget.toggle_pause)
    panel.source_changed.connect(change_camera_source)
    panel.visibility_toggled.connect(widget.setVisible)
    
    # Arah B: Floating Widget -> Panel Kontrol
    widget.resized.connect(panel.set_size_value)
    widget.pause_changed.connect(panel.set_paused_state)
    
    # Alat Coretan Layar (Screen Brush)
    # Arah A: Panel Kontrol -> Overlay
    panel.brush_mode_toggled.connect(brush_overlay.set_drawing_enabled)
    panel.brush_width_changed.connect(brush_overlay.set_pen_width)
    panel.brush_color_changed.connect(brush_overlay.set_pen_color)
    panel.brush_undo_requested.connect(brush_overlay.undo)
    panel.brush_clear_requested.connect(brush_overlay.clear_all)
    panel.brush_tool_changed.connect(brush_overlay.set_tool_mode)

    # Arah B: Overlay -> Panel Kontrol (Sinkronisasi Dua Arah)
    brush_overlay.drawing_toggled.connect(panel.set_brush_enabled)
    brush_overlay.tool_changed.connect(panel.set_brush_tool)
    brush_overlay.color_changed.connect(panel.set_brush_color)
    brush_overlay.width_changed.connect(panel.set_brush_width)

    # 4. Inisialisasi source kamera pertama saat startup
    initial_source = "mock" if args.mock else "webcam"
    initial_index = args.camera
    change_camera_source(initial_source, initial_index)

    # Sinkronisasi status awal pada panel kontrol
    panel.set_size_value(widget.width())
    panel.set_opacity_value(widget.windowOpacity())
    panel.set_mirror_checked(widget.is_mirror_mode())
    panel.set_paused_state(widget.is_paused())

    # 5. Posisikan Window berdampingan secara elegan di kanan layar
    screen = app.primaryScreen().geometry()
    
    # Floating widget di pojok kanan atas
    widget.move(screen.width() - widget.width() - 40, 40)
    widget.show()
    
    # Panel kontrol di sebelah kiri floating widget
    panel.move(screen.width() - widget.width() - panel.width() - 80, 40)
    panel.show()
    
    # Menghubungkan tombol tutup panel kontrol untuk keluar dari seluruh aplikasi
    panel.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
    
    # Overlay coretan di layar dimulai dalam keadaan tersembunyi (hidden) secara default
    
    # Run loop
    exit_code = app.exec()
    
    # Bersihkan thread saat aplikasi keluar
    if active_thread is not None:
        active_thread.stop()
        active_thread.wait()
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
