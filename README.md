# 🎬 Muf Studio

Aplikasi desktop studio presentasi dengan fitur **floating webcam**, **screen annotation**, dan **control panel** — dibangun dengan PyQt6 untuk Windows.

![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.11-green?logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-Private-red)
![Tests](https://img.shields.io/badge/Tests-53%20passed-brightgreen)

## ✨ Fitur Utama

### 🎥 Floating Webcam
- Window webcam **mengambang (always-on-top)** tanpa border
- Bisa digeser (**drag**) dan di-resize (**scroll wheel**)
- **Mirror mode** (flip horizontal) untuk tampilan natural
- **Pause/Resume** feed kamera
- Sudut membulat (**rounded corners**) dengan anti-aliasing
- Mendukung **multi-source**: Webcam Device 0/1 dan Mock Camera

### ✏️ Screen Annotation
- **Pen tool** — Menggambar coretan bebas di atas layar dengan warna neon
- **Text tool** — Menambahkan anotasi teks floating di posisi klik
- **5 warna neon**: Pink, Cyan, Green, Yellow, White
- **Undo & Clear** — Batalkan coretan terakhir atau hapus semua
- **Ketebalan pen** yang bisa diatur (2px — 20px)
- Mendukung **multi-monitor** — overlay muncul di layar tempat kursor berada

### 🎛️ Control Panel
- Panel kontrol terpisah untuk mengatur semua parameter
- **Sinkronisasi dua arah** antara panel kontrol, webcam, dan overlay
- Pengaturan: opacity, ukuran, mirror, pause, source kamera
- Pengaturan annotation: toggle, tool, warna, ketebalan, undo, clear

### 🔧 Annotation Toolbar
- Toolbar mengambang di atas overlay saat mode annotation aktif
- Akses cepat ke tool, warna, undo, clear, dan close
- Top-level window terpisah — selalu bisa diklik di atas overlay

## 🏗️ Arsitektur

```
muf_studio/
├── camera.py              # Service kamera (OpenCV + Mock)
├── gui.py                 # Floating webcam widget
├── control_panel.py       # Panel kontrol utama
├── screen_brush.py        # Overlay anotasi layar
└── annotation_toolbar.py  # Toolbar floating anotasi

main.py                    # Entry point & signal coordination
tests/                     # Test suite (53 test cases)
docs/                      # Dokumentasi & laporan AI
```

### Prinsip Desain
- **SOLID** — Setiap modul memiliki tanggung jawab tunggal
- **Signal-Slot** — Komunikasi antar komponen via PyQt signals (decoupled)
- **Top-Level Windows** — Toolbar dan text input sebagai window independen (menghindari bug focus Windows DWM)
- **TDD** — Semua fitur dikembangkan dengan Test-Driven Development

### Diagram Arsitektur

```
┌─────────────────┐     signals      ┌──────────────────┐
│  ControlPanel   │◄────────────────►│  FloatingWebcam  │
│    Window       │                  │     Widget       │
└────────┬────────┘                  └──────────────────┘
         │ signals
         ▼
┌─────────────────┐     signals      ┌──────────────────┐
│  ScreenBrush    │◄────────────────►│   Annotation     │
│    Overlay      │                  │    Toolbar       │
│  (fullscreen)   │                  │  (top-level)     │
└────────┬────────┘                  └──────────────────┘
         │ creates
         ▼
┌─────────────────┐
│   Text Input    │
│   (top-level    │
│    popup)       │
└─────────────────┘
```

## 🚀 Instalasi & Menjalankan

### Prasyarat
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Webcam (opsional — bisa pakai Mock Camera)

### Setup

```bash
# Clone repository
git clone https://github.com/mufidhadi/muf-studio.git
cd muf-studio

# Install dependencies
uv sync
```

### Menjalankan Aplikasi

```bash
# Menggunakan webcam default (device 0)
uv run main.py

# Menggunakan Mock Camera (tanpa webcam fisik)
uv run main.py --mock

# Menggunakan webcam device tertentu
uv run main.py --camera 1

# Mengatur FPS
uv run main.py --fps 60
```

### CLI Options

| Flag | Deskripsi | Default |
|------|-----------|---------|
| `-c`, `--camera` | Indeks device kamera | `0` |
| `-m`, `--mock` | Gunakan Mock Camera | `false` |
| `-f`, `--fps` | Frame rate per detik | `30` |

## 🧪 Testing

```bash
# Jalankan semua test
uv run pytest

# Jalankan test dengan output verbose
uv run pytest -v

# Jalankan test file tertentu
uv run pytest tests/test_screen_brush.py -v

# Jalankan test class tertentu
uv run pytest tests/test_overlay_focus_fix.py::TestOverlayDoesNotStealFocus -v
```

### Test Coverage

| Test File | Jumlah Test | Cakupan |
|-----------|-------------|---------|
| `test_camera.py` | 1 | Mock camera service |
| `test_gui.py` | 5 | Floating webcam widget |
| `test_control_panel.py` | 13 | Panel kontrol & signal |
| `test_screen_brush.py` | 19 | Overlay, toolbar, stroke, text |
| `test_integration.py` | 3 | Sinkronisasi bi-directional |
| `test_overlay_focus_fix.py` | 6 | Focus management overlay |
| `test_text_input_keyboard.py` | 9 | Keyboard input text annotation |
| **Total** | **53** | — |

## 🎨 Keyboard Shortcuts

| Shortcut | Aksi |
|----------|------|
| Klik Kiri (pada webcam) | Drag/pindahkan window |
| Scroll Wheel (pada webcam) | Resize window |
| Klik Kanan (pada webcam) | Menu konteks |

## 📁 Struktur Project

```
D:\project\mufid\muf_studio\
├── main.py                    # Entry point aplikasi
├── pyproject.toml             # Konfigurasi project & dependencies
├── uv.lock                   # Lock file dependencies
├── README.md                  # Dokumentasi utama (file ini)
│
├── muf_studio/                # Source code utama
│   ├── __init__.py
│   ├── camera.py              # CameraInterface, OpenCVCameraService, MockCameraService
│   ├── gui.py                 # FloatingWebcamWidget
│   ├── control_panel.py       # ControlPanelWindow
│   ├── screen_brush.py        # ScreenBrushOverlay
│   └── annotation_toolbar.py  # AnnotationToolbarWindow
│
├── tests/                     # Test suite
│   ├── test_camera.py
│   ├── test_gui.py
│   ├── test_control_panel.py
│   ├── test_screen_brush.py
│   ├── test_integration.py
│   ├── test_overlay_focus_fix.py
│   └── test_text_input_keyboard.py
│
└── docs/                      # Dokumentasi
    ├── planning_floating_webcam.md
    ├── architecture.md
    └── ai_report/             # Laporan AI per task
        ├── 001_floating_webcam.md
        ├── 002_screen_annotation_text.md
        ├── 005_fix_overlay_focus_stealing_toolbar_unclickable.md
        └── 006_fix_text_input_keyboard_blocked.md
```

## 📝 Dependencies

| Package | Versi | Kegunaan |
|---------|-------|----------|
| `pyqt6` | ≥6.11.0 | Framework GUI desktop |
| `opencv-python` | ≥4.13.0 | Capture dan pemrosesan video kamera |
| `pytest` | ≥9.1.1 | Framework testing |
| `pytest-qt` | ≥4.5.0 | Plugin pytest untuk testing PyQt |

## 📋 Catatan Teknis Penting

### Windows DWM & Focus Management
Aplikasi ini menangani beberapa quirk khusus Windows:

1. **`WA_TranslucentBackground` + child widget** — Child widget di dalam window transparan gagal menerima mouse events di Windows. Solusi: gunakan top-level window terpisah (lihat `AnnotationToolbarWindow`).

2. **`WindowDoesNotAcceptFocus`** — Flag ini mencegah overlay mencuri focus dari toolbar, tapi juga memblokir keyboard input pada child widget. Solusi: text input dibuat sebagai popup window terpisah.

3. **Z-order management** — Menggunakan `raise_()` dan `activateWindow()` secara selektif pada komponen yang tepat untuk menjaga z-order yang benar.

## 📄 Lisensi

Private — Hak cipta Mufid Hadi.
