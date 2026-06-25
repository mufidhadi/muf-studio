import time
import pytest
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QImage
from muf_studio.camera import MockCameraService

def test_mock_camera_service_emits_frames(qtbot):
    """Menguji bahwa MockCameraService memancarkan frame QImage ketika berjalan."""
    # Ensure QCoreApplication exists (handled by qtbot)
    service = MockCameraService(fps=30)
    
    frames_received = []
    
    def on_frame(qimage):
        frames_received.append(qimage)
        
    service.frame_received.connect(on_frame)
    
    # Mulai service
    with qtbot.wait_signal(service.frame_received, timeout=1000):
        service.start()
        
    # Periksa bahwa kita menerima setidaknya satu frame dan tipe datanya benar
    assert len(frames_received) > 0
    assert isinstance(frames_received[0], QImage)
    assert not frames_received[0].isNull()
    
    # Hentikan service
    service.stop()
    service.wait(1000)
    assert not service.isRunning()
