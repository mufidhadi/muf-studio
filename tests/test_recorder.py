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
    success = recorder.start_recording(monitor_idx=0, output_path=output_path, audio_device_idx=0)
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

def test_mss_screen_recorder_get_audio_devices():
    recorder = MSSScreenRecorder()
    devices = recorder.get_available_audio_devices()
    assert isinstance(devices, list)
    for dev in devices:
        assert "index" in dev
        assert "name" in dev
        assert "channels" in dev

def test_mss_screen_recorder_merge_audio_video_sync_offset():
    from unittest.mock import patch
    recorder = MSSScreenRecorder()
    
    # Kasus 1: video mulai belakangan dibanding audio (video_start > audio_start)
    # offset > 0 -> video tunda audio: -itsoffset sebelum audio_path
    with patch("subprocess.run") as mock_run, \
         patch("os.path.exists", return_value=True), \
         patch("os.remove"):
        
        recorder.temp_video_path = "temp_video.mp4"
        recorder.temp_audio_path = "temp_audio.wav"
        recorder.final_output_path = "final.mp4"
        
        recorder._merge_audio_video("temp_video.mp4", "temp_audio.wav", "final.mp4", video_start=10.5, audio_start=10.0)
        
        called_args = mock_run.call_args[0][0]
        # index "temp_audio.wav" harus didahului "-itsoffset" "0.500"
        idx_audio = called_args.index("temp_audio.wav")
        assert called_args[idx_audio - 1] == "-i"
        assert called_args[idx_audio - 2] == "0.500"
        assert called_args[idx_audio - 3] == "-itsoffset"
        
    # Kasus 2: audio mulai belakangan dibanding video (video_start < audio_start)
    # offset < 0 -> audio tunda video: -itsoffset sebelum video_path
    with patch("subprocess.run") as mock_run, \
         patch("os.path.exists", return_value=True), \
         patch("os.remove"):
        
        recorder._merge_audio_video("temp_video.mp4", "temp_audio.wav", "final.mp4", video_start=10.0, audio_start=10.5)
        
        called_args = mock_run.call_args[0][0]
        # index "temp_video.mp4" harus didahului "-itsoffset" "0.500"
        idx_video = called_args.index("temp_video.mp4")
        assert called_args[idx_video - 1] == "-i"
        assert called_args[idx_video - 2] == "0.500"
        assert called_args[idx_video - 3] == "-itsoffset"
