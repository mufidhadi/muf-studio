# Laporan Akhir Pengerjaan: Floating Webcam GUI

Laporan ini mendokumentasikan pengerjaan pembuatan aplikasi Window GUI Webcam Mengambang (*Floating Webcam*) yang bersifat *borderless*, selalu di atas (*always-on-top*), persegi (*square*), dapat digeser (*draggable*), serta diubah ukurannya (*scalable*).

---

## 1. Detail Informasi Tugas
*   **Nama Tugas:** Pembuatan Window GUI Floating Webcam
*   **Nama Branch:** `feature/floating-webcam`
*   **Nomor Hash Commit:** `5abcb7f9e74dd43a18d656b84c3479b734779804`
*   **Nama & URL Repo:** Local Repository (`D:\project\mufid\muf_studio`)
*   **Tech Stack:**
    *   Python (CPython >= 3.12)
    *   PyQt6 (GUI Library)
    *   OpenCV (`opencv-python` untuk pemrosesan kamera)
    *   Numpy (Pengolahan array gambar mock)
    *   Pytest & Pytest-QT (Untuk Test-Driven Development)
    *   Uv (Python package & environment manager)

---

## 2. Histori Aksi
1.  **Brainstorming & Pencarian Referensi:** Menganalisis cara membuat window frameless, stays-on-top, serta cara menggambar frame video dengan sudut membulat (*rounded corners*) menggunakan PyQt6 dan OpenCV.
2.  **Perencanaan & Persetujuan:** Membuat dokumen perencanaan di `docs/planning_floating_webcam.md` dan meminta persetujuan mas mufid.
3.  **Membuat Branch:** Membuat branch khusus `feature/floating-webcam` dari branch master.
4.  **Instalasi Dependencies:** Menggunakan `uv add` untuk menginstal `pyqt6`, `opencv-python`, `pytest`, dan `pytest-qt`.
5.  **Pembuatan Unit Test & GUI Test (TDD):**
    *   Menulis `tests/test_camera.py` untuk memverifikasi logika camera service.
    *   Menulis `tests/test_gui.py` untuk menguji inisialisasi window flags, mirror mode, status pause/resume, dan opacity.
6.  **Implementasi Modul Kamera (`camera.py`):**
    *   Membuat abstraksi `CameraInterface`.
    *   Mengimplementasikan `MockCameraService` (memancarkan animasi kotak memantul neon untuk test & fallback).
    *   Mengimplementasikan `OpenCVCameraService` untuk membaca feed kamera nyata dan memotongnya secara persegi di tengah (*center-crop*).
7.  **Implementasi Modul GUI (`gui.py`):**
    *   Membuat `FloatingWebcamWidget` dengan flag `FramelessWindowHint` dan `WindowStaysOnTopHint`.
    *   Menerapkan *custom paint event* menggunakan `QPainterPath` untuk sudut melengkung yang mulus tanpa membocorkan sudut persegi video.
    *   Menambahkan interaksi menggeser window (*dragging*) dan scroll mouse untuk mengubah ukuran persegi (*resizing*) yang terpusat.
    *   Menyediakan menu klik kanan (context menu) bernuansa gelap premium untuk Pause, Mirror, Opacity, Switch Camera Source, dan Exit.
8.  **Menjalankan Test Suite:** Menjalankan `uv run pytest` dan memastikan semua test suite hijau/lulus (5 passed).
9.  **Integrasi di `main.py`:** Menghubungkan GUI dengan thread kamera dan menguji aplikasi secara langsung.
10. **Penambahan Fitur Drag Resize (TDD):**
    *   Menambahkan test case `test_gui_drag_resize` untuk memverifikasi drag resize pada pojok kanan bawah.
    *   Mengimplementasikan penanganan mouse hover (merubah kursor ke diagonal grip) dan penyeretan (*drag-to-resize*) pada pojok kanan bawah window.
    *   Menambahkan dekorasi visual berupa 3 baris grip diagonal di pojok kanan bawah agar pengguna mengenali area *resize*.
11. **Dokumentasi & Commit:** Menyimpan perubahan kode ke Git dan membuat laporan akhir ini.

---

## 3. Kesulitan, Tantangan, Bug dan Solusi
*   **Kesulitan:** Penggunaan QPainter dengan font tertentu di dalam thread kamera non-GUI menyebabkan crash bertuliskan `QFontDatabase: Must construct a QGuiApplication before accessing QFontDatabase`.
    *   *Solusi:* Memindahkan seluruh logika penggambaran UI Mock (teks & bentuk) ke OpenCV (`cv2.putText` dan `cv2.rectangle`) pada sisi numpy array sebelum dikonversi menjadi `QImage`. Ini menjaga thread kamera sepenuhnya terisolasi dari Qt GUI engine, terbukti 100% aman saat dijalankan di pengujian headless pytest, serta meningkatkan performa rendering.
*   **Tantangan:** Menjaga agar rasio window tetap persegi saat di-resize menggunakan mouse scroll maupun penyeretan manual.
    *   *Solusi:* 
        *   Untuk scroll: Menggunakan fungsi `wheelEvent` untuk mendeteksi scroll, menambah/mengurangi dimensi secara proporsional (persegi), serta menyesuaikan posisi geometri agar pusat window tetap diam (*centered scaling*).
        *   Untuk penyeretan: Menggunakan `mousePressEvent`/`mouseMoveEvent` dengan membatasi ukuran baru mengikuti `max(x, y)` dari koordinat lokal kursor, menjaga window tetap 1:1, dan menggambarkan grip visual.
*   **UX WebCam:** Gambar kamera biasanya terasa janggal bagi pengguna jika tidak memiliki efek cermin (*mirroring*).
    *   *Solusi:* Menambahkan mode pencerminan horizontal secara default (`frame.mirrored(True, False)`) yang bisa diaktifkan/dinonaktifkan melalui menu klik kanan.

---

## 4. Lesson Learned
*   Pembuatan modul terpisah (SOLID) antara *business logic* (camera thread) dengan *presentation layer* (GUI widget) sangat memudahkan pembuatan mock object untuk keperluan pengujian.
*   Menghindari inisialisasi objek-objek GUI Qt (seperti `QFont`, `QPainter` pada layar utama) di dalam thread terpisah dapat meningkatkan stabilitas aplikasi secara signifikan dan menghindari error aneh pada memory segment Qt.
*   Pengolahan data mentah gambar di OpenCV lebih disarankan sebelum dikonversi ke tipe data representatif GUI.
