# Laporan Akhir Pengerjaan: Coretan dan Tulisan Layar (Screen Annotation & Text Tool)

Laporan ini mendokumentasikan pengerjaan pembuatan fitur baru berupa alat untuk membuat coretan dan tulisan secara interaktif di layar fullscreen menggunakan overlay transparan.

---

## 1. Detail Informasi Tugas
*   **Nama Tugas:** Penambahan Fitur Coretan & Tulisan di Layar (Screen Annotation)
*   **Nama Branch:** `feature/screen-annotation-text`
*   **Nomor Hash Commit:** `07c2ed5beadf84ad2164d09abefc1aec338da69f`
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
7.  **Menambahkan Test Multi-Monitor & DPI (TDD):**
    *   Menambahkan unit test `test_screen_brush_multimonitor_geometry` untuk memverifikasi keselarasan penempatan overlay berdasarkan letak kursor.
8.  **Penyempurnaan Overlay (`screen_brush.py`):**
    *   Mengubah penentuan ukuran overlay menggunakan `QGuiApplication.screenAt(QCursor.pos())` agar dinamis mengikuti letak kursor mouse pada sistem multi-monitor.
    *   Meningkatkan alpha background penutup dari `1` menjadi `5` (`QColor(0, 0, 0, 5)`) agar aman dari pembulatan interpolasi DWM saat Windows DPI Scaling aktif.
9.  **Eksekusi Test Suite (TDD - Green Phase):** Menjalankan pengujian menggunakan `uv run pytest` dan memastikan semua test suite hijau/lulus (27 passed).
10. **Pembersihan & Komit:** Menyimpan seluruh file perubahan ke Git dengan hash commit tercantum di atas.

---

## 3. Kesulitan, Tantangan, Bug dan Solusi
*   **Kesulitan:** Menyediakan form input teks yang ergonomis langsung pada titik klik tanpa merusak estetika dan transparansi layar overlay.
    *   *Solusi:* Menggunakan `QLineEdit` borderless semi-transparan dengan border tipis bertitik (dashed line) berwarna neon seirama warna pen aktif. QLineEdit ini diposisikan tepat pada koordinat klik mouse, secara otomatis memegang fokus input, dan hancur (`WA_DeleteOnClose`) seketika input teks dikonfirmasi (melalui tombol Enter/Esc/Klik di tempat lain). Teks tersebut kemudian digambar sebagai representasi raster permanen pada `paintEvent`.
*   **Tantangan:** Mengintegrasikan Undo dan Clear All agar bekerja untuk coretan garis dan anotasi tulisan sekaligus.
    *   *Solusi:* Menyimpan data anotasi tulisan ke dalam list data terpadu `self.strokes` dengan menambahkan metadata `"type": "text"`. Hal ini membuat fungsi `undo()` dan `clear_all()` dapat mengontrol histori aksi secara linear dan seragam tanpa membutuhkan logika histori terpisah.
*   **Bug & Solusi Desain:** Mode anotasi layar awalnya tidak merespons klik mouse (stuck click-through) dan kursor tidak berubah karena mengubah status click-through secara dinamis (`WA_TransparentForMouseEvents` dan `WindowTransparentForInput`) pada top-level window sangat tidak stabil di OS Windows.
    *   **Tantangan Eksklusif Fullscreen Windows:** Pada Windows OS, memanggil `showFullScreen()` pada window translucent akan memaksa DWM (Desktop Window Manager) melewati composition untuk window tersebut demi performa (menjadikannya "exclusive fullscreen"). Akibat dari bypass composition ini adalah:
        1. Fitur transparansi/translucency dinonaktifkan secara paksa oleh OS, membuat window menjadi hitam atau tidak digambar sama sekali.
        2. Window manager Windows memblokir input focus karena window bertindak sebagai aplikasi eksklusif, sehingga kursor tidak berubah dan klik mouse tidak masuk ke Qt overlay.
    *   **Solusi Akhir (Arsitektur Overlay Geometri Desktop + Show/Hide Dinamis):**
        *   **Mengganti `showFullScreen()` dengan Geometry Manual:** Alih-alih memanggil `showFullScreen()`, kita menggunakan window frameless biasa (`FramelessWindowHint | WindowStaysOnTopHint | Tool`) yang geometrinya secara manual diatur agar menutupi seluruh layar utama via `self.setGeometry(QApplication.primaryScreen().geometry())`, kemudian ditampilkan menggunakan `self.show()`. Hal ini menjaga DWM Windows composition tetap aktif sehingga transparansi tetap 100% bekerja.
        *   **Saat menggambar aktif:** Overlay window ditampilkan menggunakan `self.show()`, `self.raise_()`, dan `self.activateWindow()`. Window menutupi layar secara visual, berada paling depan, dan menangkap semua klik mouse (tanpa flag click-through) sehingga coretan/tulisan dapat dibuat dan kursor crosshair (✏️) bekerja sempurna.
        *   **Saat menggambar nonaktif:** Overlay window langsung disembunyikan menggunakan `self.hide()`. Karena window disembunyikan, input mouse otomatis jatuh 100% ke desktop/aplikasi di bawahnya tanpa hambatan.
        *   **Penyimpanan State:** Seluruh coretan dan tulisan tetap disimpan di memory (`self.strokes`). Saat overlay ditampilkan kembali (`show()`), seluruh coretan langsung dirender ulang secara instan oleh `paintEvent`. Model ini 100% stabil di Windows, bebas dari lag handle re-creation, dan sangat andal.
*   **Bug Multi-Monitor & DPI Scaling:**
    *   **Tantangan Multi-Monitor:** Pemosisian overlay secara statis pada `primaryScreen()` membuat window overlay tidak muncul ketika Control Panel dan kursor berada di monitor sekunder.
    *   *Solusi:* Menggunakan `QGuiApplication.screenAt(QCursor.pos())` untuk mendeteksi posisi kursor secara dinamis dan menempatkan overlay tepat di monitor aktif tempat user ingin menggambar.
    *   **Tantangan DPI Scaling Click-Through:** Dengan penataan DPI Scaling Windows (seperti 125% atau 150%), interpolasi tekstur layered window dapat membulatkan nilai transparansi alpha `1` (`QColor(0, 0, 0, 1)`) menjadi `0`, yang mengakibatkan OS mendeteksinya sebagai pixel kosong dan melempar klik mouse (click-through) sehingga kursor crosshair tidak muncul.
    *   *Solusi:* Meningkatkan alpha warna dasar background transparan menjadi `5` (`QColor(0, 0, 0, 5)`). Opacity ~1.96% ini terbukti 100% aman terhadap pemotongan rounding interpolasi OS, namun tetap tidak kasat mata oleh mata manusia.

---

## 4. Lesson Learned
*   Dengan merancang skema data histori gambar yang polimorfik (membedakan jenis element dari properti `"type"`), manipulasi state seperti Undo dan Clear All menjadi sangat mudah dan meminimalisir kemungkinan terjadinya inkonsistensi status aplikasi.
*   Pemisahan logika penulisan teks dinamis (memanfaatkan QLineEdit bawaan Qt) dan representasi statis (memakai painter drawText) merupakan pendekatan terbaik untuk menjaga efisiensi memori dan responsivitas interaksi mouse di layar.
