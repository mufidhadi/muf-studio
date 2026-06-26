# Laporan Akhir: Memperbaiki Lokasi Penyimpanan Rekaman Video Executable (Frozen)

## Nama Tugas
Memperbaiki & Menjelaskan Lokasi Penyimpanan Rekaman Video saat Menjalankan Aplikasi dari File Executable (.exe)

## Histori Aksi
1. Mengubah kode `main.py` dengan menambahkan fungsi `get_recordings_dir()` untuk mendeteksi apakah aplikasi berjalan dari executable terkompilasi (`sys.frozen`) atau script python biasa.
2. Memperbarui `start_screen_recording()` agar menggunakan path dinamis yang dihasilkan oleh `get_recordings_dir()`.
3. Menjalankan seluruh regression tests (`uv run pytest`) untuk memastikan tidak ada perubahan yang merusak fitur lainnya (60/60 lulus).
4. Membuat branch baru `fix/recordings-path-exe` agar perubahan tidak merusak branch utama secara langsung.
5. Melakukan commit perubahan dan melakukan push branch baru ke remote repository GitHub.

## Nomor Hash Commit
`338273aa66dd6b6ba97a926ab97219f41dd4e524`

## Nama Branch
`fix/recordings-path-exe`

## Nama dan URL Repo
- Nama Repo: `mufidhadi/muf-studio`
- URL Repo: `https://github.com/mufidhadi/muf-studio.git`

## Tech Stack
- Python 3.12
- PyQt6 (GUI Framework)
- OpenCV-Python (Video Processing)
- MSS (Screen Capturing)
- SoundDevice & SoundFile (Audio Recording)
- PyInstaller (Executable Packager)
- Pytest (Testing Framework)
- UV (Python Package Manager & Runner)

## List Kesulitan, Tantangan, Bug dan Solusi
- **Kesulitan / Tantangan**: Menentukan di mana file rekaman video harus disimpan ketika aplikasi dibungkus menjadi single executable `.exe`.
- **Bug**: Jika menggunakan path absolut file script (`__file__`), PyInstaller dalam mode `--onefile` akan mengekstrak file ke folder temporary runtime (`AppData\Local\Temp\_MEIxxxxxx`). Hal ini mengakibatkan file rekaman video tersimpan di folder temporary tersebut dan hilang begitu aplikasi ditutup.
- **Solusi**: Menggunakan `sys.frozen` untuk memeriksa status aplikasi. Jika frozen, kita menggunakan `os.path.dirname(sys.executable)` untuk mengambil folder tempat file `.exe` dijalankan, lalu membuat subfolder `recordings/` di lokasi tersebut. Jika tidak frozen (development mode), aplikasi akan jatuh kembali menggunakan folder `recordings/` di root proyek.

## Lesson Learned
- Selalu pisahkan pendeteksian asset internal (yang berada di dalam bundle exe, menggunakan `sys._MEIPASS`) dengan penulisan file eksternal/output (yang harus berada di luar bundle exe, menggunakan `sys.executable`).
- Membuat branch baru sebelum melakukan commit perubahan pada branch utama agar mengikuti standar clean-workflow.
