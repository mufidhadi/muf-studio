import os
import time
import cv2
import numpy as np
import mss
import queue
import sounddevice as sd
import soundfile as sf
import threading
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class ScreenRecorderInterface:
    """Interface untuk fitur perekam layar (Screen Recorder) dengan audio."""
    
    def start_recording(self, monitor_idx: int, output_path: str, audio_device_idx: int = -1) -> bool:
        """Memulai perekaman layar pada monitor tertentu dan opsional dengan audio input."""
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

    def get_available_audio_devices(self) -> list:
        """Mengembalikan daftar perangkat audio input yang tersedia."""
        raise NotImplementedError

class MockScreenRecorder(ScreenRecorderInterface):
    """Implementasi Mock Screen Recorder untuk kebutuhan unit testing."""
    
    def __init__(self):
        self._is_recording = False
        self.start_time = 0
        self.stop_time = 0

    def start_recording(self, monitor_idx: int, output_path: str, audio_device_idx: int = -1) -> bool:
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

    def get_available_audio_devices(self) -> list:
        return [
            {"index": 0, "name": "Mock Microphone 1", "channels": 2}
        ]

class AudioRecorder(threading.Thread):
    """Thread terpisah untuk merekam audio dari perangkat input terpilih ke berkas WAV."""
    
    def __init__(self, device_idx: int, output_path: str, sample_rate: int = 44100, channels: int = 2):
        super().__init__()
        self.device_idx = device_idx
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_queue = queue.Queue()
        self._is_running = True
        self.error_message = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())

    def run(self):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
            
            # Setup input stream
            stream = sd.InputStream(
                device=self.device_idx,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._callback
            )
            
            # Setup output WAV file
            with sf.SoundFile(self.output_path, mode='w', samplerate=self.sample_rate, channels=self.channels) as file:
                with stream:
                    while self._is_running or not self.audio_queue.empty():
                        try:
                            # Gunakan timeout pendek agar thread responsif terhadap sinyal stop
                            data = self.audio_queue.get(timeout=0.1)
                            file.write(data)
                        except queue.Empty:
                            continue
        except Exception as e:
            self.error_message = str(e)
            print(f"Audio recording thread error: {e}")

    def stop(self):
        self._is_running = False

class RecorderThread(QThread):
    """Thread terpisah untuk menangkap frame layar dan menyimpannya ke video dengan kecepatan normal."""
    
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
                if self.monitor_idx + 1 >= len(sct.monitors):
                    self.error_occurred.emit("Monitor index out of range")
                    return
                
                monitor = sct.monitors[self.monitor_idx + 1]
                width = monitor["width"]
                height = monitor["height"]
                
                # Inisialisasi VideoWriter
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))
                
                if not out.isOpened():
                    self.error_occurred.emit("Failed to initialize VideoWriter")
                    return
                
                delay = 1.0 / self.fps
                start_time = time.perf_counter()
                frames_written = 0
                
                while self._is_running:
                    loop_start = time.perf_counter()
                    
                    # Capture frame layar
                    sct_img = sct.grab(monitor)
                    img = np.array(sct_img)
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # Hitung target frame yang seharusnya tertulis di video berdasarkan elapsed time
                    # Ini mencegah efek "video dipercepat" jika capture rate tidak pas 30 FPS
                    elapsed = time.perf_counter() - start_time
                    target_frames = int(elapsed * self.fps) + 1
                    
                    # Tulis frame (mungkin duplikasi jika kita tertinggal)
                    while frames_written < target_frames:
                        out.write(frame)
                        frames_written += 1
                        
                    # Hitung waktu sisa untuk mempertahankan target FPS
                    elapsed_loop = time.perf_counter() - loop_start
                    sleep_time = delay - elapsed_loop
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    else:
                        time.sleep(0.001) # Mencegah monopolasi CPU
                        
                out.release()
                self.finished_successfully.emit(self.output_path)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False

class MSSScreenRecorder(ScreenRecorderInterface):
    """Implementasi riil Screen Recorder menggunakan mss, sounddevice, OpenCV, dan ffmpeg."""
    
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.thread = None
        self.audio_recorder = None
        self.start_time = 0
        self.stop_time = 0
        self.final_output_path = None
        self.temp_video_path = None
        self.temp_audio_path = None

    def start_recording(self, monitor_idx: int, output_path: str, audio_device_idx: int = -1) -> bool:
        if self.is_recording():
            return False
            
        self.final_output_path = output_path
        self.start_time = time.time()
        
        if audio_device_idx != -1:
            # Jika menggunakan audio, rekam video dan audio ke file temporer terlebih dahulu
            self.temp_video_path = output_path + ".temp_video.mp4"
            self.temp_audio_path = output_path + ".temp_audio.wav"
            
            # Jalankan video recorder
            self.thread = RecorderThread(monitor_idx, self.temp_video_path, self.fps)
            self.thread.start()
            
            # Jalankan audio recorder
            self.audio_recorder = AudioRecorder(audio_device_idx, self.temp_audio_path)
            self.audio_recorder.start()
        else:
            # Jika tanpa audio, rekam langsung ke file final
            self.temp_video_path = None
            self.temp_audio_path = None
            self.audio_recorder = None
            self.thread = RecorderThread(monitor_idx, output_path, self.fps)
            self.thread.start()
            
        return True

    def stop_recording(self):
        # Stop video thread
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
            self.thread = None
            
        # Stop audio thread
        if self.audio_recorder and self.audio_recorder.is_alive():
            self.audio_recorder.stop()
            self.audio_recorder.join()
            self.audio_recorder = None
            
        self.stop_time = time.time()
        
        # Merge audio & video jika diperlukan
        if self.temp_video_path and self.temp_audio_path and self.final_output_path:
            self._merge_audio_video(self.temp_video_path, self.temp_audio_path, self.final_output_path)
            self.temp_video_path = None
            self.temp_audio_path = None
            
    def _merge_audio_video(self, video_path, audio_path, final_path):
        try:
            # Command ffmpeg untuk merge video dan audio tanpa re-encoding video
            # -y menimpa file yang sudah ada
            # -c:v copy menyalin data video secara langsung
            # -c:a aac mengompresi audio WAV menjadi format AAC
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                final_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            
            # Hapus file temporer jika berhasil
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            print(f"FFmpeg merge error: {e}")
            # Fallback: jika merge gagal, ganti nama berkas video temporer menjadi berkas final (tanpa audio)
            if os.path.exists(video_path):
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(video_path, final_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)

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

    def get_available_audio_devices(self) -> list:
        try:
            devices = sd.query_devices()
            audio_devices = []
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    audio_devices.append({
                        "index": i,
                        "name": dev['name'],
                        "channels": dev['max_input_channels']
                    })
            return audio_devices
        except Exception as e:
            print(f"Error querying audio devices: {e}")
            return []
