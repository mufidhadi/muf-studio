import os
import time
import pytest
from muf_studio.recorder import (
    ScreenRecorderInterface,
    MockScreenRecorder,
    MSSScreenRecorder
)

def test_screen_recorder_interface_exists():
    assert issubclass(MockScreenRecorder, ScreenRecorderInterface)
    assert issubclass(MSSScreenRecorder, ScreenRecorderInterface)

def test_mock_screen_recorder_lifecycle(tmp_path):
    recorder = MockScreenRecorder()
    assert not recorder.is_recording()
    assert recorder.get_elapsed_time() == 0
    
    # Start recording
    output_path = str(tmp_path / "dummy.mp4")
    success = recorder.start_recording(monitor_idx=0, output_path=output_path)
    assert success
    assert recorder.is_recording()
    
    # Wait a bit
    time.sleep(1.1)
    assert recorder.get_elapsed_time() >= 1
    
    # Stop recording
    recorder.stop_recording()
    assert not recorder.is_recording()

def test_mss_screen_recorder_get_monitors():
    recorder = MSSScreenRecorder()
    monitors = recorder.get_available_monitors()
    assert len(monitors) >= 1
    for m in monitors:
        assert "index" in m
        assert "name" in m
        assert "width" in m
        assert "height" in m
