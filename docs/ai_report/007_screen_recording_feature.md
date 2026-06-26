# Laporan Akhir: Implementasi Fitur Screen Recording dengan Dukungan Multi-Monitor

## Nama Tugas
Implementasi fitur screen recording yang dapat merekam keseluruhan layar. Jika sistem mendeteksi ada lebih dari 1 layar, memberikan opsi pada panel kontrol untuk memilih layar monitor mana yang ingin direkam.

## Histori Aksi
1. **Perencanaan & Analisis**: Membuat dokumen rencana pengembangan di [planning_screen_recording.md](file:///D:/project/mufid/muf_studio/docs/planning_screen_recording.md).
2. **Penambahan Dependensi**: Menambahkan library `mss` untuk penangkapan layar berkecepatan tinggi dengan perintah `uv add mss`.
3. **Pengembangan TDD (Red & Green Phase - Unit Test)**:
   - Menulis pengujian unit di [test_recorder.py](file:///D:/project/mufid/muf_studio/tests/test_recorder.py).
   - Mengimplementasikan `ScreenRecorderInterface`, `MSSScreenRecorder`, dan `MockScreenRecorder` di [recorder.py](file:///D:/project/mufid/muf_studio/muf_studio/recorder.py).
4. **Pengembangan TDD (Red & Green Phase - GUI & Integration Test)**:
   - Menulis pengujian GUI di [test_recorder_gui.py](file:///D:/project/mufid/muf_studio/tests/test_recorder_gui.py).
   - Menambahkan elemen UI di [control_panel.py](file:///D:/project/mufid/muf_studio/muf_studio/control_panel.py) berupa ComboBox pemilihan monitor, label status waktu perekaman, dan tombol rekam.
   - Menulis pengujian integrasi dua arah di [test_integration.py](file:///D:/project/mufid/muf_studio/tests/test_integration.py).
5. **Integrasi Utama**: Menghubungkan perekam layar riil di [main.py](file:///D:/project/mufid/muf_studio/main.py) dengan event-handling dan otomatisasi penyimpanan berkas di folder `recordings/` dengan pola nama `recording_YYYYMMDD_HHMMSS.mp4`.
6. **Verifikasi & Pembersihan**: Mematikan dan membersihkan data dummy keluaran hasil testing menggunakan fixture pytest `tmp_path`, serta memastikan seluruh 59 pengujian passed.

## Nomor Hash Commit
`9e3dbc5`

## Nama Branch
`feature/screen-recording`

## Nama dan URL Repo
- **Nama Repo**: `mufidhadi/muf-studio`
- **URL Repo**: [https://github.com/mufidhadi/muf-studio.git](https://github.com/mufidhadi/muf-studio.git)

## Tech Stack
- Python 3.12+
- PyQt6 (GUI Framework)
- mss (High-performance screen capture library)
- opencv-python (Video encoding - `cv2.VideoWriter`)
- numpy (Format manipulasi matriks frame)
- pytest & pytest-qt (Testing frameworks)

## List Kesulitan, Tantangan, Bug dan Solusi
1. **Pemetaan Indeks Monitor**:
   - *Masalah*: Indeks monitor pada Qt dimulai dari `0` untuk monitor fisik pertama. Namun pada `mss`, indeks `0` merupakan representasi dari virtual screen gabungan (union of all screens), sedangkan monitor fisik dimulai dari indeks `1`.
   - *Solusi*: Melakukan konversi pemetaan indeks dengan menambahkan offset `1` (`monitor_idx + 1`) sebelum memanggil fungsionalitas capture `mss`.
2. **Deprecation Warnings mss.mss()**:
   - *Masalah*: Penggunaan `mss.mss()` memunculkan peringatan depresiasi pada pytest suite.
   - *Solusi*: Mengganti instansiasi context manager ke `mss.MSS()`.
3. **Pembersihan File Dummy Pengujian**:
   - *Masalah*: Tes awal menghasilkan file `dummy.mp4` secara lokal di dalam folder workspace.
   - *Solusi*: Menggunakan fixture pytest `tmp_path` untuk membuat file sementara yang secara otomatis dibersihkan oleh pytest setelah pengujian selesai.

## Lesson Learn
- **Multithreading di PyQt**: Tugas intensif I/O seperti menangkap frame monitor dan menyandikannya ke format MP4 (melalui OpenCV) harus diisolasi di thread terpisah (`QThread`) agar frame rate perekaman konsisten (30 FPS) dan GUI thread utama bebas dari lag atau freeze.
- **SOLID & Mocking**: Penerapan Interface (`ScreenRecorderInterface`) memudahkan pengujian fungsionalitas GUI secara terpisah menggunakan `MockScreenRecorder` tanpa harus bergantung pada API display head nyata sistem, yang sangat berguna pada lingkungan server CI/CD headless.
