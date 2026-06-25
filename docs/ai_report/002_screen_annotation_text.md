# Laporan Akhir Pengerjaan: Coretan dan Tulisan Layar (Screen Annotation & Text Tool)

Laporan ini mendokumentasikan pengerjaan pembuatan fitur baru berupa alat untuk membuat coretan dan tulisan secara interaktif di layar fullscreen menggunakan overlay transparan.

---

## 1. Detail Informasi Tugas
*   **Nama Tugas:** Penambahan Fitur Coretan & Tulisan di Layar (Screen Annotation)
*   **Nama Branch:** `feature/screen-annotation-text`
*   **Nomor Hash Commit:** `08587264297d149539e29494d8d95ebcdc63bf93`
*   **Nama & URL Repo:** mufidhadi/muf-studio (https://github.com/mufidhadi/muf-studio)
*   **Tech Stack:**
    *   Python (CPython >= 3.12)
    *   PyQt6 (GUI Library)
    *   Pytest & Pytest-QT (Untuk Test-Driven Development)
    *   Uv (Python package & environment manager)

---

## 2. Histori Aksi
1.  **Brainstorming & Pencarian Referensi:** Menganalisis cara merancang input teks interaktif di atas overlay transparan PyQt6 agar tidak mengganggu klik-through pada desktop ketika mode coretan tidak aktif.
2.  **Membuat Branch:** Berpindah ke branch baru `feature/screen-annotation-text` dari branch `main` demi menjaga kebersihan alur kerja git.
3.  **Pembuatan Unit Test (TDD - Red Phase):**
    *   Menambahkan unit test `test_screen_brush_tool_mode`, `test_screen_brush_text_annotation`, dan `test_screen_brush_text_undo_clear` di [tests/test_screen_brush.py](file:///D:/project/mufid/muf_studio/tests/test_screen_brush.py).
    *   Menambahkan unit test `test_control_panel_brush_tool_selection` di [tests/test_control_panel.py](file:///D:/project/mufid/muf_studio/tests/test_control_panel.py).
    *   Menambahkan integration test untuk koordinasi pemilihan tool di [tests/test_integration.py](file:///D:/project/mufid/muf_studio/tests/test_integration.py).
4.  **Implementasi Coretan & Tulisan Layar (`screen_brush.py`):**
    *   Membuat properti `tool_mode` (nilai default `"pen"`, nilai alternatif `"text"`).
    *   Mengimplementasikan `set_tool_mode` untuk mengontrol pergantian tool.
    *   Mengimplementasikan pembuatan editor teks dinamis `QLineEdit` di koordinat posisi klik mouse kiri saat berada pada mode `"text"`.
    *   Menghubungkan signal `editingFinished` dari editor teks agar secara otomatis menyimpan anotasi tulisan ke dalam list `strokes` dengan tipe `"text"`.
    *   Memperbarui `paintEvent` untuk menggambar teks (`painter.drawText`) dengan ukuran font sebanding terhadap ketebalan pen saat ini.
5.  **Implementasi UI Control Panel (`control_panel.py`):**
    *   Menyediakan dua buah checkable button berdampingan: **✏️ Pen** dan **🔤 Text** di dalam GroupBox "Screen Annotation Tools".
    *   Mengelompokkan kedua tombol ke dalam `QButtonGroup` eksklusif agar bertindak layaknya radio button.
    *   Memancarkan sinyal `brush_tool_changed(str)` saat terjadi pergantian tombol aktif.
6.  **Koordinasi di `main.py`:**
    *   Menghubungkan sinyal `panel.brush_tool_changed` ke slot `brush_overlay.set_tool_mode` pada inisialisasi aplikasi.
7.  **Eksekusi Test Suite (TDD - Green Phase):** Menjalankan pengujian menggunakan `uv run pytest` dan memastikan semua test suite hijau/lulus (26 passed).
8.  **Pembersihan & Komit:** Menyimpan seluruh file perubahan ke Git dengan hash commit tercantum di atas.

---

## 3. Kesulitan, Tantangan, Bug dan Solusi
*   **Kesulitan:** Menyediakan form input teks yang ergonomis langsung pada titik klik tanpa merusak estetika dan transparansi layar overlay.
    *   *Solusi:* Menggunakan `QLineEdit` borderless semi-transparan dengan border tipis bertitik (dashed line) berwarna neon seirama warna pen aktif. QLineEdit ini diposisikan tepat pada koordinat klik mouse, secara otomatis memegang fokus input, dan hancur (`WA_DeleteOnClose`) seketika input teks dikonfirmasi (melalui tombol Enter/Esc/Klik di tempat lain). Teks tersebut kemudian digambar sebagai representasi raster permanen pada `paintEvent`.
*   **Tantangan:** Mengintegrasikan Undo dan Clear All agar bekerja untuk coretan garis dan anotasi tulisan sekaligus.
    *   *Solusi:* Menyimpan data anotasi tulisan ke dalam list data terpadu `self.strokes` dengan menambahkan metadata `"type": "text"`. Hal ini membuat fungsi `undo()` dan `clear_all()` dapat mengontrol histori aksi secara linear dan seragam tanpa membutuhkan logika histori terpisah.
*   **Bug & Solusi Desain:** Mode anotasi layar awalnya tidak merespons klik mouse (stuck click-through) karena mengubah status click-through secara dinamis (`WA_TransparentForMouseEvents` dan `WindowTransparentForInput`) pada top-level fullscreen window yang sudah ditampilkan sangat tidak stabil di OS Windows.
    *   *Solusi Akhir (Arsitektur Show/Hide Dinamis):* Alih-alih memanipulasi flag transparansi input OS secara dinamis pada window yang terus aktif, solusinya adalah menggunakan **model overlay show/hide dinamis**:
        *   **Saat menggambar aktif:** Overlay window dipanggil menggunakan `self.showFullScreen()`, `self.raise_()`, dan `self.activateWindow()`. Window ini aktif, berada paling depan, dan menangkap semua klik mouse (tanpa flag click-through) sehingga coretan/tulisan dapat dibuat.
        *   **Saat menggambar nonaktif:** Overlay window langsung disembunyikan menggunakan `self.hide()`. Karena window disembunyikan, input mouse otomatis jatuh 100% ke desktop/aplikasi di bawahnya tanpa hambatan.
        *   **Penyimpanan State:** Seluruh coretan dan tulisan tetap disimpan di memory (`self.strokes`). Saat overlay ditampilkan kembali (`showFullScreen()`), seluruh coretan akan langsung dirender ulang secara instan oleh `paintEvent`. Model ini 100% stabil di Windows, bebas dari lag handle re-creation, dan sangat andal.

---

## 4. Lesson Learned
*   Dengan merancang skema data histori gambar yang polimorfik (membedakan jenis element dari properti `"type"`), manipulasi state seperti Undo dan Clear All menjadi sangat mudah dan meminimalisir kemungkinan terjadinya inkonsistensi status aplikasi.
*   Pemisahan logika penulisan teks dinamis (memanfaatkan QLineEdit bawaan Qt) dan representasi statis (memakai painter drawText) merupakan pendekatan terbaik untuk menjaga efisiensi memori dan responsivitas interaksi mouse di layar.
