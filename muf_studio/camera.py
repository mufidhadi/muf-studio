import time
import numpy as np
import cv2
from PyQt6.QtCore import QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPen

class CameraInterface(QThread):
    """Kelas abstrak/antarmuka untuk layanan kamera."""
    frame_received = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._is_running = False

    def stop(self):
        self._is_running = False


class MockCameraService(CameraInterface):
    """
    Kamera tiruan (Mock) untuk pengujian dan fallback.
    Menghasilkan animasi persegi memantul pada layar gelap menggunakan OpenCV.
    """
    def __init__(self, fps=30, size=(400, 400)):
        super().__init__()
        self.fps = fps
        self.width, self.height = size
        self.delay = 1.0 / fps

    def run(self):
        self._is_running = True
        
        # Posisi awal persegi memantul
        box_size = 80
        x = (self.width - box_size) // 2
        y = (self.height - box_size) // 2
        dx = 4
        dy = 3

        while self._is_running:
            # 1. Buat frame hitam dengan numpy (BGR untuk OpenCV)
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            # Isi background dengan abu-abu sangat gelap (RGB #1e1e24 -> BGR [36, 30, 30])
            frame[:] = [36, 30, 30]
            
            # 2. Gambar persegi memantul (Neon Blue: RGB #00f2fe -> BGR [254, 242, 0])
            cv2.rectangle(frame, (x, y), (x + box_size, y + box_size), (254, 242, 0), 3, cv2.LINE_AA)
            
            # Tambahkan fill transparan pada box (opsional, tapi OpenCV rectangle tidak ada alpha, 
            # kita bisa lakukan blending atau biarkan saja border luar agar performansi tinggi)
            
            # Gambar teks status & waktu (Neon Green: RGB #00ff87 -> BGR [135, 255, 0])
            cv2.putText(frame, "MOCK CAMERA ACTIVE", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (135, 255, 0), 2, cv2.LINE_AA)
            
            # Waktu saat ini
            current_time = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
            cv2.putText(frame, f"Time: {current_time}", (20, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (192, 174, 160), 1, cv2.LINE_AA)
            
            cv2.putText(frame, f"FPS: {self.fps} | Size: {self.width}x{self.height}", (20, 95), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (192, 174, 160), 1, cv2.LINE_AA)
            
            # 3. Konversi BGR (OpenCV) ke RGB (Qt)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 4. Konversi ke QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qimage = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Emit frame salinan
            self.frame_received.emit(qimage.copy())

            # Update posisi box
            x += dx
            y += dy
            
            # Deteksi tabrakan dengan tepi window
            if x <= 0 or x + box_size >= self.width:
                dx = -dx
            if y <= 0 or y + box_size >= self.height:
                dy = -dy

            time.sleep(self.delay)


class OpenCVCameraService(CameraInterface):
    """
    Layanan kamera riil menggunakan OpenCV.
    Melakukan capture gambar dari webcam, melakukan cropping ke persegi,
    dan mengirimkannya ke GUI.
    """
    def __init__(self, camera_index=0, fps=30):
        super().__init__()
        self.camera_index = camera_index
        self.fps = fps
        self.delay = 1.0 / fps

    def run(self):
        self._is_running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        # Atur lebar/tinggi webcam jika didukung
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self._is_running:
            ret, frame = cap.read()
            if not ret:
                # Jika gagal membaca, beri jeda singkat dan coba lagi
                time.sleep(0.1)
                continue
            
            # 1. Potong frame agar berbentuk persegi 1:1 (Center Crop)
            h, w = frame.shape[:2]
            min_dim = min(h, w)
            start_x = (w - min_dim) // 2
            start_y = (h - min_dim) // 2
            cropped = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
            
            # 2. Konversi BGR (OpenCV) ke RGB (Qt)
            rgb_frame = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            
            # 3. Konversi ke QImage
            ch, cw = rgb_frame.shape[:2]
            bytes_per_line = 3 * cw
            qimage = QImage(rgb_frame.data, cw, ch, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Kirim frame salinan ke GUI
            self.frame_received.emit(qimage.copy())
            
            time.sleep(self.delay)

        cap.release()
