# Arsitektur Muf Studio

Dokumen ini menjelaskan arsitektur teknis, pola desain, dan alur data pada aplikasi Muf Studio.

## 1. Gambaran Umum

Muf Studio adalah aplikasi desktop PyQt6 yang terdiri dari **5 komponen utama** yang berkomunikasi via **signal-slot pattern** (decoupled):

```
┌──────────────────────────────────────────────────────────┐
│                       main.py                            │
│               (Coordinator / Wiring Layer)               │
│                                                          │
│   Menghubungkan semua signal antar komponen              │
│   Mengelola lifecycle kamera dan window                  │
└──────────┬───────────┬──────────┬───────────┬────────────┘
           │           │          │           │
           ▼           ▼          ▼           ▼
    ┌────────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────┐
    │  Control   │ │Floating │ │  Screen  │ │ Annotation  │
    │   Panel    │ │ Webcam  │ │  Brush   │ │  Toolbar    │
    │  Window    │ │ Widget  │ │ Overlay  │ │  Window     │
    └────────────┘ └─────────┘ └──────────┘ └─────────────┘
```

## 2. Komponen Detail

### 2.1 CameraService (`camera.py`)

Menyediakan abstraksi untuk capture video, berjalan pada **QThread** terpisah agar tidak memblokir GUI thread.

```
CameraInterface (Abstract / QThread)
├── OpenCVCameraService  — Kamera fisik via OpenCV
└── MockCameraService    — Animasi tiruan untuk testing
```

**Signal**: `frame_received(QImage)` — Dipancarkan setiap frame baru siap.

### 2.2 FloatingWebcamWidget (`gui.py`)

Widget utama yang menampilkan video webcam dalam window persegi, mengambang, dan borderless.

**Window Flags**: `FramelessWindowHint | WindowStaysOnTopHint | SubWindow`

**Fitur**:
- Custom `paintEvent` dengan rounded corner clipping
- Drag via `mousePressEvent` / `mouseMoveEvent`
- Resize via `wheelEvent` (scroll)
- Context menu via `contextMenuEvent`
- Mirror mode (horizontal flip)

**Signals emitted**: `resized(int)`, `pause_changed(bool)`

### 2.3 ControlPanelWindow (`control_panel.py`)

Panel kontrol terpisah sebagai "remote control" untuk seluruh aplikasi.

**Sections**:
| Section | Kontrol |
|---------|---------|
| Floating Window Settings | Opacity slider, Size slider, Mirror checkbox |
| Camera Feed Settings | Source combo, Pause button |
| Screen Annotation Tools | Toggle, Tool (Pen/Text), Width slider, Color buttons, Undo, Clear |
| Visibility | Show/Hide floating window |

**Signals emitted**: `opacity_changed`, `size_changed`, `mirror_toggled`, `pause_toggled`, `source_changed`, `visibility_toggled`, `brush_mode_toggled`, `brush_color_changed`, `brush_width_changed`, `brush_undo_requested`, `brush_clear_requested`, `brush_tool_changed`

### 2.4 ScreenBrushOverlay (`screen_brush.py`)

Overlay transparan fullscreen untuk menggambar coretan anotasi di atas layar.

**Window Flags**: `FramelessWindowHint | WindowStaysOnTopHint | Tool | WindowDoesNotAcceptFocus`

**Attributes**: `WA_TranslucentBackground`, `WA_ShowWithoutActivating`

**Desain penting**:
- Overlay **tidak pernah menerima focus** — ini mencegah overlay mencuri fokus dari toolbar
- `paintEvent` menggambar `fillRect` dengan alpha=5 agar Windows DWM menangkap mouse events
- Text input dibuat sebagai **popup window terpisah** (bukan child) agar bisa menerima keyboard input

**Signals emitted**: `drawing_toggled(bool)`, `tool_changed(str)`, `color_changed(QColor)`, `width_changed(int)`

### 2.5 AnnotationToolbarWindow (`annotation_toolbar.py`)

Toolbar floating yang muncul di atas overlay saat mode annotation aktif.

**Window Flags**: `FramelessWindowHint | WindowStaysOnTopHint | Tool`

**Desain penting**:
- **Top-level window terpisah** (tanpa parent) — bukan child dari overlay
- Ini solusi untuk bug Windows DWM dimana child widget di dalam window `WA_TranslucentBackground` tidak bisa menerima mouse events
- Guard `_updating` mencegah double-update saat sinkronisasi warna

**Signals emitted**: `close_requested`, `tool_changed(str)`, `color_changed(QColor)`, `undo_requested`, `clear_requested`

## 3. Alur Signal (Data Flow)

### 3.1 Tiga Arah Komunikasi

```
Arah A: Control Panel ──► Overlay / Webcam
Arah B: Overlay / Webcam ──► Control Panel (sinkronisasi balik)
Arah C: Toolbar ──► Overlay & Control Panel
```

### 3.2 Alur Detail: Ganti Warna dari Toolbar

```
1. User klik tombol warna di Toolbar
2. Toolbar._on_color_clicked()
   ├── Update visual border pada color buttons
   ├── Emit color_changed(QColor)
   ├── self.raise_() + self.activateWindow()
   └── QApplication.processEvents()
3. Signal diterima oleh:
   ├── brush_overlay.set_pen_color(color)
   │   ├── Update self.current_color
   │   └── toolbar.set_active_color(color)  ← guard _updating mencegah loop
   └── panel.set_brush_color(color)
       └── Update visual border pada panel color buttons
```

### 3.3 Alur Detail: Buat Text Annotation

```
1. User dalam mode "text", klik di overlay
2. overlay.mousePressEvent()
   └── overlay.create_text_input(pos)
       ├── Buat QLineEdit() sebagai TOP-LEVEL window (tanpa parent)
       ├── Set WindowFlags: Frameless + StaysOnTop + Tool
       ├── mapToGlobal(pos) untuk positioning
       ├── show() + activateWindow() + setFocus()
       └── Connect editingFinished signal
3. User mengetik teks + tekan Enter
4. QLineEdit.editingFinished signal
   └── overlay._on_text_editing_finished()
       ├── Simpan teks ke self.strokes
       ├── Close editor
       ├── set_tool_mode("pen")
       └── Emit tool_changed("pen")
```

## 4. Keputusan Arsitektur

### 4.1 Mengapa Top-Level Windows?

| Komponen | Mengapa Top-Level? |
|----------|--------------------|
| AnnotationToolbar | Child widget di dalam `WA_TranslucentBackground` window gagal menerima mouse events di Windows DWM |
| Text Input (QLineEdit) | Parent overlay memiliki `WindowDoesNotAcceptFocus` — semua child widget diblokir dari menerima keyboard focus |

### 4.2 Mengapa `WindowDoesNotAcceptFocus` pada Overlay?

Tanpa flag ini, overlay yang fullscreen akan **mencuri focus** setiap kali di-show() atau di-repaint(), menyebabkan toolbar di belakangnya tidak bisa diklik.

### 4.3 Mengapa `fillRect(alpha=5)` di paintEvent?

Windows DWM menganggap area **100% transparan** sebagai "tidak ada" untuk mouse hit-testing. Dengan mengisi background dengan alpha=5 (nyaris tak terlihat), Windows menganggap overlay sebagai area yang valid untuk menerima mouse events.

## 5. Testing Strategy

### Unit Tests
- Setiap modul memiliki test file tersendiri
- Menguji inisialisasi, state management, dan signal emission

### Integration Tests
- `test_integration.py` — Menguji sinkronisasi bi-directional antar komponen
- Mensimulasikan alur kerja nyata: klik panel → perubahan di overlay, dan sebaliknya

### Regression Tests
- `test_overlay_focus_fix.py` — Memastikan overlay tidak mencuri focus
- `test_text_input_keyboard.py` — Memastikan text input bisa menerima keyboard

### Konvensi
- Semua test menggunakan `pytest` + `pytest-qt`
- Dijalankan dengan `uv run pytest`
- Prinsip TDD: test ditulis sebelum implementasi

## 6. Known Issues & Limitations

1. **Multi-monitor coordinate mapping** — Posisi text input mungkin sedikit offset pada setup multi-monitor dengan skala DPI berbeda
2. **Escape key** — Belum ada handler untuk menutup text input via Escape key
3. **Text editing** — Hanya mendukung single-line text (QLineEdit), belum multi-line
4. **Undo granularity** — Undo menghapus seluruh stroke, bukan per-titik
