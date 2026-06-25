# Fix: Overlay Focus Stealing - Toolbar Annotation Tidak Bisa Diklik

## Nama Tugas
Fix bug: Toolbar annotation tidak bisa diklik setelah mengganti warna

## Histori Aksi

1. **Analisis kode** — Membaca `screen_brush.py`, `annotation_toolbar.py`, `control_panel.py`, dan `main.py` untuk memahami arsitektur dan signal flow
2. **Riset referensi** — Mencari di internet tentang `WA_TranslucentBackground overlay blocking mouse clicks` dan `Qt overlay window steals focus from sibling window`
3. **Root cause analysis** — Mengidentifikasi bahwa overlay memanggil `activateWindow()` dan tidak memiliki `WindowDoesNotAcceptFocus` / `WA_ShowWithoutActivating`
4. **Buat branch** — `fix/overlay-focus-stealing-toolbar-unclickable` dari `feature/screen-annotation-text`
5. **TDD RED** — Menulis 6 test case di `tests/test_overlay_focus_fix.py`, 3 test gagal (sesuai harapan)
6. **TDD GREEN** — Implementasi fix di `screen_brush.py`, semua 6 test baru lulus
7. **Regression test** — Menjalankan seluruh 44 test, semua PASSED (0 regresi)
8. **Commit** — `c71f08f`

## Nomor Hash Commit
`c71f08f`

## Nama Branch
`fix/overlay-focus-stealing-toolbar-unclickable`

## Nama dan URL Repo
- **Nama**: muf-studio
- **URL**: https://github.com/mufidhadi/muf-studio.git

## Tech Stack
- Python 3.12
- PyQt6 6.11.0
- Qt Runtime 6.11.1
- pytest 9.1.1 + pytest-qt 4.5.0
- uv (package manager)

## Root Cause Analysis

### Hipotesa Awal (Mas Mufid)
> `painter.fillRect(self.rect(), QColor(0, 0, 0, 5))` menghalangi GUI annotation toolbar

### Hasil Analisis
Hipotesa **sebagian benar** — `fillRect` bukan penyebab langsung, tapi overlay yang menutupi layar penuh memang menghalangi toolbar. Masalahnya bukan pada rendering (paint), melainkan pada **focus management dan z-order**.

### Root Cause Sesungguhnya
`ScreenBrushOverlay.set_drawing_enabled(True)` memanggil:
```python
self.show()
self.raise_()
self.activateWindow()  # <-- BUG: mencuri fokus dari toolbar
```

Ditambah overlay **TIDAK memiliki**:
- `Qt.WindowType.WindowDoesNotAcceptFocus` — sehingga overlay bisa menerima fokus
- `Qt.WidgetAttribute.WA_ShowWithoutActivating` — sehingga `show()` otomatis mengaktifkan overlay

Ketika user mengganti warna di toolbar:
1. `_on_color_clicked()` → emit `color_changed`
2. Signal chain: `brush_overlay.set_pen_color()` → `toolbar.set_active_color()`
3. `set_active_color()` memanggil `setStyleSheet()` pada semua color button
4. Qt melakukan repolish, yang **bisa memicu repaint** pada overlay
5. Karena overlay adalah active window, DWM Windows menganggap overlay berada di atas toolbar
6. Klik berikutnya pada toolbar **ditangkap oleh overlay** (bukan toolbar)

### Solusi
3 perubahan di `screen_brush.py`:

| Perubahan | Alasan |
|-----------|--------|
| Tambah `WindowDoesNotAcceptFocus` pada window flags | Overlay tidak bisa menerima keyboard/mouse focus |
| Tambah `WA_ShowWithoutActivating` attribute | `show()` tidak mencuri fokus dari toolbar |
| Hapus `activateWindow()` dari `set_drawing_enabled()` | Overlay tidak boleh jadi active window |

## List Kesulitan, Tantangan, Bug dan Solusi

| # | Masalah | Solusi |
|---|---------|--------|
| 1 | `fillRect` terlihat mencurigakan tapi bukan root cause sebenarnya | Riset mendalam ke dokumentasi Qt tentang `WA_TranslucentBackground` dan focus management |
| 2 | `activateWindow()` menyebabkan overlay menjadi active window dan mencuri fokus | Menghapus `activateWindow()` dan menambahkan `WA_ShowWithoutActivating` |
| 3 | Overlay menerima fokus saat diklik (meskipun transparan) | Menambahkan `WindowDoesNotAcceptFocus` flag |
| 4 | Test harus bisa memverifikasi "toolbar tetap clickable" tanpa display fisik | Menggunakan `qtbot.mouseClick()` dan memeriksa emisi signal sebagai proxy |

## Lesson Learn

1. **`paintEvent` dan `fillRect` BUKAN penyebab mouse blocking** — di Qt, rendering (paint) dan input handling (events) adalah dua sistem yang terpisah. `fillRect` hanya menggambar piksel, tidak mempengaruhi hit-testing.

2. **Focus management di Windows + `WA_TranslucentBackground` sangat tricky** — DWM (Desktop Window Manager) Windows memiliki perilaku khusus untuk window transparan. Window aktif selalu mendapat prioritas input, meskipun terlihat transparan.

3. **Selalu gunakan `WA_ShowWithoutActivating` untuk overlay** — Overlay yang menutupi layar penuh TIDAK boleh mencuri fokus dari window lain.

4. **`WindowDoesNotAcceptFocus` adalah pasangan wajib** — Selain `WA_ShowWithoutActivating`, flag ini memastikan overlay tidak pernah bisa menerima fokus, bahkan jika user mengklik area transparan.

5. **TDD sangat membantu** — Dengan menulis test dulu, saya bisa memverifikasi bahwa fix benar-benar menyelesaikan masalah tanpa regresi (44/44 test passed).
