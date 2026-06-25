# Fix: Text Input Tidak Bisa Menerima Keyboard di Annotation Mode

## Nama Tugas
Fix bug: Box input text muncul saat klik, tetapi keyboard tidak bisa digunakan untuk mengetik

## Histori Aksi

1. **Merge fix sebelumnya** — Merge branch `fix/overlay-focus-stealing-toolbar-unclickable` ke `main` (commit `9e3041f`)
2. **Buat branch baru** — `fix/text-input-not-receiving-keyboard`
3. **Analisis kode** — Membaca `screen_brush.py` khususnya `create_text_input()` dan flag-flag overlay
4. **Riset referensi** — Mencari di internet tentang `QLineEdit child of WindowDoesNotAcceptFocus cannot type` dan `PyQt6 floating QLineEdit popup input`
5. **Root cause teridentifikasi** — `WindowDoesNotAcceptFocus` pada overlay memblokir semua child widget dari menerima keyboard focus
6. **TDD RED** — Menulis 9 test case di `tests/test_text_input_keyboard.py`, 3 test gagal (sesuai harapan)
7. **TDD GREEN** — Implementasi fix di `screen_brush.py`, semua 9 test baru lulus
8. **Regression test** — Menjalankan seluruh 53 test, semua PASSED (0 regresi)
9. **Commit** — `4f2e194`

## Nomor Hash Commit
- Fix: `4f2e194`
- Merge sebelumnya: `9e3041f`

## Nama Branch
`fix/text-input-not-receiving-keyboard`

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

### Gejala
- Klik di mode text → box input muncul (QLineEdit visible) ✅
- Tekan keyboard → tidak ada teks yang muncul ❌

### Root Cause
Pada fix sebelumnya (`c71f08f`), kita menambahkan `WindowDoesNotAcceptFocus` flag pada `ScreenBrushOverlay` untuk mencegah overlay mencuri fokus dari toolbar. **Efek sampingnya**: flag ini juga mencegah **semua child widget** dari menerima keyboard focus.

```python
# screen_brush.py line 154 (SEBELUM fix)
self.text_editor = QLineEdit(self)  # <-- child dari overlay
#                           ^^^^
# Overlay punya WindowDoesNotAcceptFocus → QLineEdit tidak bisa terima keyboard
```

QLineEdit dibuat dengan `QLineEdit(self)` — menjadikannya child dari overlay. Karena parent (overlay) memiliki `WindowDoesNotAcceptFocus`, Qt tidak mengizinkan child widget mana pun untuk menerima keyboard focus. Widget tetap bisa di-render (visible) dan menerima mouse events, tapi **keyboard events tidak dikirim** ke widget.

### Solusi
Ubah QLineEdit dari child overlay menjadi **top-level popup window terpisah**:

```python
# screen_brush.py (SESUDAH fix)
self.text_editor = QLineEdit()  # <-- top-level, tanpa parent
self.text_editor.setWindowFlags(
    Qt.WindowType.FramelessWindowHint
    | Qt.WindowType.WindowStaysOnTopHint
    | Qt.WindowType.Tool
)
```

Pendekatan ini konsisten dengan `AnnotationToolbarWindow` yang juga top-level.

### Perubahan tambahan
| Perubahan | Alasan |
|-----------|--------|
| `QLineEdit()` tanpa parent | Menjadi top-level window yang bisa menerima focus |
| `setWindowFlags(Frameless + StaysOnTop + Tool)` | Tampil di atas overlay tanpa border |
| `mapToGlobal(pos)` untuk positioning | Konversi koordinat lokal overlay ke koordinat global layar |
| `activateWindow()` sebelum `setFocus()` | Memastikan window aktif sebelum memberi focus |

## List Kesulitan, Tantangan, Bug dan Solusi

| # | Masalah | Solusi |
|---|---------|--------|
| 1 | `WindowDoesNotAcceptFocus` memblokir semua child widget | Buat QLineEdit sebagai top-level window terpisah |
| 2 | Posisi QLineEdit salah karena bukan child lagi | Gunakan `mapToGlobal()` untuk konversi koordinat |
| 3 | QLineEdit tidak mendapat focus setelah show | Panggil `activateWindow()` lalu `setFocus()` |
| 4 | Fix ini adalah efek samping dari fix sebelumnya | Kedua fix saling mendukung — overlay tidak terima fokus, tapi text popup bisa |

## Lesson Learn

1. **Setiap fix bisa menimbulkan bug baru** — Fix `WindowDoesNotAcceptFocus` yang menyelesaikan masalah toolbar justru memblokir text input. Selalu jalankan regression test setelah setiap perubahan.

2. **Konsistensi arsitektur penting** — Saat AnnotationToolbar sudah dipisahkan jadi top-level window karena masalah focus, seharusnya text input juga langsung dipikirkan hal yang sama. Satu pattern harus diterapkan konsisten.

3. **`WindowDoesNotAcceptFocus` itu flag yang sangat agresif** — Flag ini memblokir focus untuk SEMUA child widget tanpa kecuali. Tidak ada cara untuk membuat "pengecualian" untuk child tertentu.

4. **`mapToGlobal()` wajib saat memindahkan child ke top-level** — Koordinat lokal widget (relative to parent) berbeda dengan koordinat global layar. Tanpa konversi, posisi widget akan salah.

5. **`activateWindow()` harus dipanggil sebelum `setFocus()`** — Pada Windows, window harus menjadi "active window" dulu sebelum bisa memberi focus ke widget di dalamnya.
