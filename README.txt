TUGAS PENGOLAHAN CITRA DIGITAL - FILTER SPASIAL

Isi folder:
- citra_cangkir.png : satu citra sumber yang dipakai pada semua percobaan.
- main.py           : program mean, Gaussian, median, sharpening dan statistik.
- requirements.txt : pustaka yang diperlukan.
- hasil/            : gambar hasil dan CSV statistik (dibuat setelah program dijalankan).

Cara menjalankan (Windows):
1. Pastikan Python 3.9 atau lebih baru sudah terpasang.
2. Buka terminal/PowerShell pada folder proyek.
3. Buat virtual environment (opsional tetapi disarankan):
   python -m venv .venv
   .venv\Scripts\activate
4. Instal pustaka:
   pip install -r requirements.txt
5. Jalankan:
   python main.py

Catatan: citra sumber adalah ilustrasi sintetis objek cangkir yang dibuat khusus untuk praktikum,
bukan foto dari internet. Seluruh pengujian memakai file sumber yang sama. Jika dosen meminta
foto objek nyata, ganti citra_cangkir.png dengan foto milik sendiri dan pertahankan nama file.
