# Laporan Akhir: Fitur Screen Recording dengan Dukungan Multi-Monitor & Perekaman Audio

## Nama Tugas
Implementasi fitur screen recording yang merekam keseluruhan layar. Jika sistem mendeteksi > 1 layar, sediakan opsi pemilihan layar monitor. Selain itu, perbaiki masalah kecepatan pemutaran video (framerate) agar normal dan tambahkan opsi memilih sumber input audio.

## Histori Aksi
1. **Perencanaan & Analisis**: Membuat dokumen rencana di [planning_screen_recording.md](file:///D:/project/mufid/muf_studio/docs/planning_screen_recording.md).
2. **Penambahan Dependensi**: Menambahkan library `mss`, `sounddevice`, dan `soundfile` menggunakan `uv add`.
3. **Pengembangan Unit & GUI Test (TDD)**:
   - Membuat dan memperbarui unit test di [test_recorder.py](file:///D:/project/mufid/muf_studio/tests/test_recorder.py) untuk memverifikasi lifecycle perekam, daftar monitor, dan daftar perangkat audio.
   - Membuat GUI test di [test_recorder_gui.py](file:///D:/project/mufid/muf_studio/tests/test_recorder_gui.py) untuk memastikan ComboBox monitor dan ComboBox audio input beroperasi dengan benar.
4. **Implementasi Perekam Layar & Waktu Presisi**:
   - Memperbarui [recorder.py](file:///D:/project/mufid/muf_studio/muf_studio/recorder.py) untuk mengimplementasikan kontrol frame rate berbasis waktu nyata (`time.perf_counter()`) dengan metode catch-up (duplikasi frame jika tertinggal) agar kecepatan pemutaran video normal 1.0x.
   - Menambahkan kelas `AudioRecorder` berbasis `threading.Thread` untuk menangkap input audio mikrofon secara asinkron ke file WAV temporer menggunakan library `sounddevice` dan `soundfile`.
5. **Merge Audio-Video dengan FFmpeg**:
   - Menambahkan fungsi utility di [recorder.py](file:///D:/project/mufid/muf_studio/muf_studio/recorder.py) untuk menggabungkan file video (.mp4) dan audio (.wav) temporer menggunakan utilitas `ffmpeg` dengan opsi penyalinan video instan (`-c:v copy`) dan kompresi audio (`-c:a aac`) untuk performa tinggi tanpa kehilangan kualitas.
6. **Integrasi UI & Uji Coba**:
   - Menambahkan dropdown audio input di [control_panel.py](file:///D:/project/mufid/muf_studio/muf_studio/control_panel.py).
   - Menghubungkan perekaman audio dan penentuan file keluaran temporer di [main.py](file:///D:/project/mufid/muf_studio/main.py).
   - Menguji integrasi dua arah di [test_integration.py](file:///D:/project/mufid/muf_studio/tests/test_integration.py) dan memverifikasi seluruh 60 pengujian passed.

## Nomor Hash Commit
- `9e3dbc5` (feat: implement screen recording with multi-monitor selection)
- `4c5dc56` (fix: normal video framerate and add audio input device selection)

## Nama Branch
`feature/screen-recording`

## Nama dan URL Repo
- **Nama Repo**: `mufidhadi/muf-studio`
- **URL Repo**: [https://github.com/mufidhadi/muf-studio.git](https://github.com/mufidhadi/muf-studio.git)

## Tech Stack
- Python 3.12+
- PyQt6 (GUI Framework)
- mss (High-performance screen capture)
- sounddevice & soundfile (Asynchronous PCM audio capture & WAV writing)
- opencv-python (Video frame packaging)
- ffmpeg (High-performance audio-video stream merging)
- numpy (Frame matrices)
- pytest & pytest-qt (Testing)

## List Kesulitan, Tantangan, Bug dan Solusi
1. **Video Terasa Dipercepat (Fast Playback)**:
   - *Masalah*: Loop capture biasa tidak memperhitungkan latensi CPU/disk write yang membuat penulisan frame lebih lambat daripada target FPS. Hal ini menyebabkan total frame yang dihasilkan sedikit, tetapi `cv2.VideoWriter` memutarnya kembali dengan kecepatan penuh (terasa seperti *fast-forward*).
   - *Solusi*: Menggunakan metode pelacakan waktu berjalan (`time.perf_counter()`) untuk menghitung target frame yang seharusnya tertulis. Jika capture rate turun, thread akan menulis ulang (menduplikasi) frame terakhir untuk catch-up sehingga kecepatan video tetap 1.0x konstan.
2. **Perekaman Audio & Penggabungan Tanpa Delay**:
   - *Masalah*: Menulis audio ke berkas video secara real-time tidak didukung oleh OpenCV. Perekaman audio juga harus responsif dan tidak memblokir penulisan video.
   - *Solusi*: Mengambil input audio di thread tersendiri (`AudioRecorder`) ke berkas `.temp_audio.wav` menggunakan buffer asinkron (`queue.Queue`). Setelah perekaman selesai, berkas video dan audio temporer digabungkan dalam fraksi detik via `ffmpeg` menggunakan command `ffmpeg -i temp_video.mp4 -i temp_audio.wav -c:v copy -c:a aac final.mp4`.
3. **Penyisihan File Sampah**:
   - *Masalah*: Proses merge audio/video menghasilkan berkas temporer `.temp_video.mp4` dan `.temp_audio.wav` di workspace.
   - *Solusi*: Menambahkan rutin penghapusan berkas temporer secara otomatis setelah proses penggabungan selesai, serta memetakan pola ignore berkas media `.mp4`, `.wav`, dan folder `recordings/` di berkas `.gitignore`.

## Lesson Learn
- Penggunaan `ffmpeg` eksternal melalui `subprocess` jauh lebih efisien untuk proses muxing/demuxing di Python daripada memasukkan dependensi video-processing berat (seperti moviepy) yang menambah ratusan megabyte ke package size.
- Penggunaan dynamic catch-up timing sangat krusial dalam pembuatan perekam layar (screen recorder) berbasis software murni untuk mengatasi hardware choke pada sistem berspesifikasi rendah.
