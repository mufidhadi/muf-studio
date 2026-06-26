# Laporan Akhir: Memperbaiki Sinkronisasi Audio-Video (Desync) pada Rekaman Layar

## Nama Tugas
Memperbaiki Masalah Desinkronisasi (Desync) antara Audio dan Video pada Fitur Perekaman Layar

## Histori Aksi
1. Menganalisis penyebab lag/desync antara rekaman video dan audio (gerakan mulut tidak selaras dengan suara).
2. Memperbaiki inisialisasi perekaman di `muf_studio/recorder.py` dengan menambahkan pencatatan waktu mulai presisi tinggi (`time.perf_counter()`) pada `AudioRecorder` (di callback pertama saat hardware mic aktif) dan `RecorderThread` (saat frame video pertama akan ditulis).
3. Mengukur selisih waktu (`offset = video_start - audio_start`) pada saat perekaman dihentikan di `MSSScreenRecorder.stop_recording()`.
4. Menerapkan opsi `-itsoffset` secara dinamis pada perintah FFmpeg saat proses penggabungan (merge) file temporer video dan audio agar menyesuaikan delay awal secara akurat tanpa melakukan re-encoding video.
5. Menulis unit test tambahan `test_mss_screen_recorder_merge_audio_video_sync_offset` di `tests/test_recorder.py` untuk menguji asersi argumen FFmpeg `-itsoffset` pada berbagai kondisi offset (video mulai belakangan atau audio mulai belakangan).
6. Menjalankan seluruh regression tests (`uv run pytest`) untuk memastikan stabilitas (61/61 lulus 100%).

## Nomor Hash Commit
`059e5025a1e2f7f98d4dcf9cb030a59929f9e160`

## Nama Branch
`fix/audio-video-sync`

## Nama dan URL Repo
- Nama Repo: `mufidhadi/muf-studio`
- URL Repo: `https://github.com/mufidhadi/muf-studio.git`

## Tech Stack
- Python 3.12
- PyQt6 (GUI Framework)
- OpenCV-Python (Video Processing)
- MSS (Screen Capturing)
- SoundDevice & SoundFile (Audio Recording)
- FFmpeg (A/V Muxing & Syncing)
- Pytest (Testing)
- UV (Python Package Manager & Runner)

## List Kesulitan, Tantangan, Bug dan Solusi
- **Kesulitan / Tantangan**: Inisialisasi library OpenCV VideoWriter dan sounddevice InputStream bergantung pada driver hardware dan OS Windows yang kecepatannya tidak bisa diprediksi secara konstan. Hal ini mengakibatkan selisih waktu awal (start offset) antara audio dan video yang tidak menentu.
- **Bug**: Ketidakselarasan konstan antara suara (audio) dan gerakan mulut (video) akibat perbedaan start time inisialisasi awal thread.
- **Solusi**: Menggunakan `time.perf_counter()` sebagai Master Clock monolitik untuk mengukur offset waktu awal secara presisi, kemudian menerapkannya ke FFmpeg dengan `-itsoffset` sebelum input video (jika video telat) atau input audio (jika audio telat).

## Lesson Learned
- Menggabungkan dua thread hardware independen (video capture & audio capture) memerlukan pencatatan timestamp real-time monolitik eksternal untuk mengoreksi offset inisialisasi.
- Menggunakan `-itsoffset` pada input FFmpeg jauh lebih cepat dibanding filter audio/video karena FFmpeg bisa menyalin stream (`-c:v copy`) langsung tanpa perlu decoding dan encoding ulang video.
