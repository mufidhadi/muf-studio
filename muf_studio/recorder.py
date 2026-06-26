import os
import time
import cv2
import numpy as np
import mss
from PyQt6.QtCore import QThread, pyqtSignal

class ScreenRecorderInterface:
    """Interface untuk fitur perekam layar (Screen Recorder)."""
    
    def start_recording(self, monitor_idx: int, output_path: str) -> bool:
        """Memulai perekaman layar pada monitor tertentu."""
        raise NotImplementedError
        
    def stop_recording(self):
        """Menghentikan perekaman layar."""
        raise NotImplementedError
        
    def is_recording(self) -> bool:
        """Mengembalikan True jika sedang melakukan perekaman."""
        raise NotImplementedError
        
    def get_elapsed_time(self) -> int:
        """Mengembalikan durasi waktu perekaman dalam detik."""
        raise NotImplementedError
        
    def get_available_monitors(self) -> list:
        """Mengembalikan daftar monitor yang terhubung."""
        raise NotImplementedError

class MockScreenRecorder(ScreenRecorderInterface):
    """Implementasi Mock Screen Recorder untuk kebutuhan unit testing."""
    
    def __init__(self):
        self._is_recording = False
        self.start_time = 0
        self.stop_time = 0

    def start_recording(self, monitor_idx: int, output_path: str) -> bool:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # Tulis data tiruan untuk mensimulasikan file output video
        with open(output_path, "wb") as f:
            f.write(b"mock video frame data")
        self._is_recording = True
        self.start_time = time.time()
        return True

    def stop_recording(self):
        if self._is_recording:
            self._is_recording = False
            self.stop_time = time.time()

    def is_recording(self) -> bool:
        return self._is_recording

    def get_elapsed_time(self) -> int:
        if self._is_recording:
            return int(time.time() - self.start_time)
        return int(self.stop_time - self.start_time) if self.start_time else 0

    def get_available_monitors(self) -> list:
        return [
            {"index": 0, "name": "Mock Monitor 1", "width": 1920, "height": 1080}
        ]

class RecorderThread(QThread):
    """Thread terpisah untuk menangkap frame layar dan menyimpannya ke video."""
    
    finished_successfully = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, monitor_idx: int, output_path: str, fps: int = 30):
        super().__init__()
        self.monitor_idx = monitor_idx
        self.output_path = output_path
        self.fps = fps
        self._is_running = True

    def run(self):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
            
            with mss.MSS() as sct:
                # sct.monitors[0] adalah virtual screen (gabungan seluruh monitor)
                # Monitor fisik dimulai dari index 1
                if self.monitor_idx + 1 >= len(sct.monitors):
                    self.error_occurred.emit("Monitor index out of range")
                    return
                
                monitor = sct.monitors[self.monitor_idx + 1]
                width = monitor["width"]
                height = monitor["height"]
                
                # Inisialisasi VideoWriter dengan format MP4
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))
                
                if not out.isOpened():
                    self.error_occurred.emit("Failed to initialize VideoWriter")
                    return
                
                delay = 1.0 / self.fps
                
                while self._is_running:
                    loop_start = time.perf_counter()
                    
                    # Ambil frame layar
                    sct_img = sct.grab(monitor)
                    
                    # Konversi ke NumPy array
                    img = np.array(sct_img)
                    
                    # Konversi format warna BGRA ke BGR (format OpenCV)
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # Tulis frame ke file video
                    out.write(frame)
                    
                    # Jaga FPS stabil
                    elapsed = time.perf_counter() - loop_start
                    sleep_time = delay - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        
                out.release()
                self.finished_successfully.emit(self.output_path)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False

class MSSScreenRecorder(ScreenRecorderInterface):
    """Implementasi riil Screen Recorder menggunakan library mss dan OpenCV."""
    
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.thread = None
        self.start_time = 0
        self.stop_time = 0

    def start_recording(self, monitor_idx: int, output_path: str) -> bool:
        if self.is_recording():
            return False
            
        self.thread = RecorderThread(monitor_idx, output_path, self.fps)
        self.start_time = time.time()
        self.thread.start()
        return True

    def stop_recording(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
            self.stop_time = time.time()
            self.thread = None

    def is_recording(self) -> bool:
        return self.thread is not None and self.thread.isRunning()

    def get_elapsed_time(self) -> int:
        if self.is_recording():
            return int(time.time() - self.start_time)
        return int(self.stop_time - self.start_time) if self.start_time else 0

    def get_available_monitors(self) -> list:
        with mss.MSS() as sct:
            monitors = []
            for i, m in enumerate(sct.monitors[1:]):
                monitors.append({
                    "index": i,
                    "name": f"Monitor {i+1}",
                    "width": m["width"],
                    "height": m["height"]
                })
            return monitors
