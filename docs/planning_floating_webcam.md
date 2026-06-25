# Rencana Pengembangan Floating Webcam GUI

Dokumen ini berisi rencana arsitektur modular, strategi pengujian, dan visual design untuk aplikasi GUI Webcam Mengambang (Floating Webcam).

## 1. Kebutuhan Fungsional & Non-Fungsional
*   **Window Mengambang (Always on Top):** Window harus tetap berada di atas aplikasi lain.
*   **Tanpa Border (Frameless):** Tidak memiliki title bar bawaan OS agar terlihat modern dan minimalis.
*   **Persegi (Square):** Window berbentuk persegi dengan sudut membulat (*rounded corners*).
*   **Bisa Digeser (Draggable):** Pengguna dapat memindahkan window dengan menekan tombol mouse kiri dan menggesernya.
*   **Bisa Di-resize (Scalable):** Pengguna dapat mengubah ukuran window secara dinamis (misalnya menggunakan scroll mouse) dan tetap menjaga aspek rasio persegi.
*   **Menu Navigasi/Konteks (Context Menu):** Klik kanan untuk memunculkan menu untuk:
    *   Pause/Resume kamera.
    *   Mirror mode (balik horizontal).
    *   Mengatur opacity/transparansi window.
    *   Memilih source input (Kamera Real vs Mock Camera).
    *   Keluar (Exit) dari aplikasi.
*   **Aman & Teruji (TDD):** Menggunakan `pytest` dan `pytest-qt` untuk menguji logika bisnis kamera dan interaksi GUI dasar.

## 2. Desain Arsitektur (SOLID)
Aplikasi ini akan dipecah menjadi beberapa modul terpisah:

### A. `camera.py` (Modul Kamera)
*   **`CameraInterface` (Abstraction):** Menyediakan antarmuka standar untuk mematikan/menghidupkan kamera dan mengirimkan frame.
*   **`OpenCVCameraService` (Implementation):** Implementasi kamera nyata menggunakan OpenCV dan `QThread` agar pembacaan frame tidak memblokir GUI thread.
*   **`MockCameraService` (Implementation):** Implementasi kamera tiruan untuk kebutuhan testing dan fallback ketika tidak ada hardware kamera fisik. Menghasilkan frame buatan dengan animasi sederhana.

### B. `gui.py` (Modul Tampilan)
*   **`FloatingWebcamWidget` (Widget):** Widget utama PyQt6 yang mengurus:
    *   Penghapusan border dan pengaturan *always-on-top*.
    *   Event drag & drop (mouse press/move).
    *   Event wheel scroll untuk mengubah ukuran (resize).
    *   *Custom paint event* dengan kliping sudut membulat untuk merender frame video.
    *   Menu konteks klik kanan.

### C. `main.py` (Entrypoint)
*   Menginisialisasi `QApplication`.
*   Menghubungkan `CameraService` ke `FloatingWebcamWidget`.
*   Menerima parameter baris perintah (CLI) seperti source indeks kamera.

---

## 3. Strategi Pengujian (Test Driven Development)
Pengujian akan dilakukan menggunakan `pytest` dan `pytest-qt`.

1.  **Unit Test Kamera (`tests/test_camera.py`):**
    *   Menguji bahwa `MockCameraService` dapat memproduksi frame (sinyal dipancarkan).
    *   Menguji status aktif/nonaktif dari service.
2.  **GUI Test (`tests/test_gui.py`):**
    *   Menguji inisialisasi widget (flags frameless, translucent, stays-on-top).
    *   Menguji fungsi toggle mirror, pause, dan perubahan opacity.
    *   Menguji resize melalui mouse wheel scroll.

---

## 4. Rencana Langkah Pengerjaan
1.  **Langkah 1:** Buat file pengujian awal (`tests/test_camera.py` & `tests/test_gui.py`) yang mendefinisikan ekspektasi (TDD).
2.  **Langkah 2:** Tulis file `camera.py` untuk mengimplementasikan antarmuka kamera & mock service agar tes awal lulus.
3.  **Langkah 3:** Tulis file `gui.py` dengan mock frame render untuk melewatkan tes GUI.
4.  **Langkah 4:** Tulis `main.py` untuk mengintegrasikan kamera riil dan mock.
5.  **Langkah 5:** Uji coba fungsionalitas secara langsung di sistem operasi Windows.
6.  **Langkah 6:** Buat laporan akhir di `docs/ai_report/xxx_floating_webcam.md`.
