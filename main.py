import sys
import argparse
from PyQt6.QtWidgets import QApplication
from muf_studio.camera import MockCameraService, OpenCVCameraService
from muf_studio.gui import FloatingWebcamWidget

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
    
    # 2. Inisialisasi Tampilan Widget
    widget = FloatingWebcamWidget()
    
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
        else:
            print(f"Beralih ke Webcam Device {index}...")
            active_thread = OpenCVCameraService(camera_index=index, fps=fps)
            
        # Hubungkan sinyal frame baru ke widget
        active_thread.frame_received.connect(widget.update_frame)
        active_thread.start()

    # Daftarkan callback switch camera ke widget
    widget.on_camera_source_changed = change_camera_source

    # 4. Inisialisasi source kamera pertama saat startup
    initial_source = "mock" if args.mock else "webcam"
    initial_index = args.camera
    change_camera_source(initial_source, initial_index)

    # 5. Tampilkan Widget dan jalankan event loop
    # Posisikan window di pojok kanan atas layar secara default sebagai UX yang baik
    screen = app.primaryScreen().geometry()
    widget.move(screen.width() - widget.width() - 40, 40)
    
    widget.show()
    
    # Run loop
    exit_code = app.exec()
    
    # Bersihkan thread saat aplikasi keluar
    if active_thread is not None:
        active_thread.stop()
        active_thread.wait()
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
