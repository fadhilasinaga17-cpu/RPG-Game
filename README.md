# Petualangan Logika - RPG Edukasi (Python + pygame)

Jalankan di laptop (VS Code):  `pip install pygame`  lalu  `python main.py`
Jadikan web untuk HP:          `pip install pygbag`  lalu  `pygbag --build main.py`  (hasil di build/web/)
Hosting gratis: itch.io (upload zip build/web, tipe HTML) atau GitHub Pages. Di HP: Chrome -> "Tambahkan ke layar utama".
(Langkah lengkap sama seperti game Ular.)

## Ganti materi
Edit `DATA_SOAL` di main.py: (pertanyaan, [4 pilihan], index_benar, penjelasan). Satu kunci = satu monster.

## Struktur OOP (untuk dijelaskan ke dosen)
| Class | Tugas |
|-------|-------|
| Pertanyaan | satu soal; mengacak pilihan & mengingat jawaban benar |
| Monster | nama, HP, soal miliknya, status kalah |
| Pemain | posisi, HP, level |
| Peta | grid, tembok, daftar monster (dibaca dari list string PETA) |
| Game | state (intro/jelajah/battle/menang), input, update, gambar |
Game *memiliki* Peta, Pemain, dan Monster (komposisi).
Alur battle: jawab benar -> Monster.terluka(); jawab salah -> Pemain.terluka(); HP 0 -> menang/kalah.
