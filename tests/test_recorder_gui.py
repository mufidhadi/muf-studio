import pytest
from PyQt6.QtCore import Qt
from muf_studio.control_panel import ControlPanelWindow

def test_recording_ui_elements_exist(qtbot):
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    # Verifikasi bahwa elemen UI kontrol perekaman layar ada
    assert hasattr(panel, "recording_group")
    assert hasattr(panel, "monitor_combo")
    assert hasattr(panel, "audio_combo")
    assert hasattr(panel, "record_button")
    assert hasattr(panel, "record_status_label")

def test_recording_signals_emitted(qtbot):
    panel = ControlPanelWindow()
    qtbot.addWidget(panel)
    
    # Simulasikan pengaturan daftar monitor
    panel.set_available_monitors([
        {"index": 0, "name": "Monitor 1", "width": 1920, "height": 1080},
        {"index": 1, "name": "Monitor 2", "width": 1280, "height": 720}
    ])
    
    assert panel.monitor_combo.count() == 2
    panel.monitor_combo.setCurrentIndex(1)
    
    # Test ketika tombol ditekan saat idle -> memicu start_recording_requested dengan index monitor terpilih
    with qtbot.waitSignal(panel.start_recording_requested) as blocker:
        qtbot.mouseClick(panel.record_button, Qt.MouseButton.LeftButton)
    assert blocker.args == [1, -1]
    
    # Simulasikan transisi status perekaman menjadi aktif
    panel.set_recording_state(True)
    assert panel.record_button.text() == "🛑 Stop Recording"
    
    # Test ketika tombol ditekan saat aktif -> memicu stop_recording_requested
    with qtbot.waitSignal(panel.stop_recording_requested) as blocker:
        qtbot.mouseClick(panel.record_button, Qt.MouseButton.LeftButton)
        
    # Simulasikan transisi status perekaman kembali ke idle
    panel.set_recording_state(False)
    assert panel.record_button.text() == "⏺ Start Recording"
