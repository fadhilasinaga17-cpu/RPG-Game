"""
PETUALANGAN LOGIKA - RPG Edukasi (Python + pygame)
Tugas PBO: memakai class, object, enkapsulasi, dan komposisi.

Cerita : Kamu Pahlawan Logika. Kalahkan 3 monster gerbang logika
         (AND, OR, NOT), lalu hadapi Raja XOR!
Cara   : Jelajahi peta, sentuh monster -> battle berupa kuis.
         Jawab benar = monster terluka. Jawab salah = kamu terluka.
Kontrol: HP -> tombol panah di layar / ketuk jawaban
         Laptop -> tombol panah atau WASD, angka 1-4 untuk jawab

Kompatibel dengan pygbag (async loop) supaya jalan di browser HP.
Untuk mengganti materi: edit bagian DATA_SOAL di bawah.
"""
import asyncio
import random

import pygame

# ---------------------------------------------------------------
# KONSTANTA
# ---------------------------------------------------------------
KOTAK = 28
KOLOM, BARIS = 15, 13
LEBAR = KOLOM * KOTAK                 # 420
HEADER = 50
PETA_Y = HEADER                       # peta mulai dari y = 50
TINGGI = 660
FPS = 60
JEDA_JALAN = 160                      # ms antar langkah saat tombol ditahan

BG = (30, 34, 50)
RUMPUT_1, RUMPUT_2 = (120, 190, 110), (110, 180, 100)
POHON, BATANG = (40, 110, 60), (110, 75, 45)
PUTIH, HITAM = (255, 255, 255), (30, 30, 40)
EMAS, MERAH, HIJAU = (250, 205, 80), (230, 70, 80), (90, 200, 120)
PANEL, TOMBOL, TOMBOL_AKTIF = (50, 56, 80), (75, 85, 125), (110, 125, 180)

# Peta: # = pohon (tembok), . = rumput, P = pemain,
#       A/O/N/X = monster AND / OR / NOT / XOR (X = bos)
PETA = [
    "###############",
    "#P....#.......#",
    "#.##..#..##.A.#",
    "#.##.....##...#",
    "#....##.......#",
    "#.O..##..####.#",
    "#........#....#",
    "###.####.#.##.#",
    "#.....#..#.#..#",
    "#.N...#....#.X#",
    "#.....#..###..#",
    "#.............#",
    "###############",
]

# ---------------------------------------------------------------
# DATA SOAL : (pertanyaan, [pilihan], index_jawaban_benar, penjelasan)
# Ganti/tambah soal di sini untuk materi lain.
# ---------------------------------------------------------------
DATA_SOAL = {
    "A": [  # AND
        ("Hasil dari 1 AND 0 adalah?", ["0", "1", "10", "Error"], 0,
         "AND hanya bernilai 1 jika SEMUA input bernilai 1."),
        ("Gerbang AND menghasilkan 1 jika...", ["Salah satu input 1", "Semua input 1", "Semua input 0", "Input berbeda"], 1,
         "AND = 'dan': semua syarat harus terpenuhi."),
        ("Di Python, True and False = ?", ["True", "False", "None", "Error"], 1,
         "True and False menghasilkan False."),
        ("Hasil dari 1 AND 1 adalah?", ["0", "1", "2", "Error"], 1,
         "Kedua input 1, jadi hasil AND = 1."),
        ("Pada tabel kebenaran AND 2 input, berapa baris yang hasilnya 1?", ["1", "2", "3", "4"], 0,
         "Hanya baris 1 AND 1 yang hasilnya 1."),
    ],
    "O": [  # OR
        ("Hasil dari 1 OR 0 adalah?", ["0", "1", "10", "Error"], 1,
         "OR bernilai 1 jika minimal satu input bernilai 1."),
        ("Gerbang OR menghasilkan 0 hanya jika...", ["Semua input 0", "Semua input 1", "Salah satu input 0", "Input berbeda"], 0,
         "OR = 0 hanya saat semua input 0."),
        ("Di Python, False or True = ?", ["True", "False", "None", "Error"], 0,
         "or bernilai True jika salah satu True."),
        ("Pada tabel kebenaran OR 2 input, berapa baris yang hasilnya 1?", ["1", "2", "3", "4"], 2,
         "01, 10, dan 11 menghasilkan 1; hanya 00 yang hasilnya 0."),
        ("Hasil dari 0 OR 0 adalah?", ["0", "1", "2", "Error"], 0,
         "Tidak ada input 1, jadi hasil OR = 0."),
    ],
    "N": [  # NOT
        ("Hasil dari NOT 1 adalah?", ["0", "1", "2", "Error"], 0,
         "NOT membalik nilai: 1 menjadi 0."),
        ("Hasil dari NOT 0 adalah?", ["0", "1", "2", "Error"], 1,
         "NOT membalik nilai: 0 menjadi 1."),
        ("Di Python, not True = ?", ["True", "False", "None", "Error"], 1,
         "not membalik True menjadi False."),
        ("Gerbang NOT juga disebut...", ["Inverter", "Penjumlah", "Pengali", "Pembanding"], 0,
         "NOT = inverter karena membalik (invert) sinyal."),
        ("NOT(NOT 1) = ?", ["0", "1", "2", "Error"], 1,
         "Dua kali dibalik kembali ke nilai awal (hukum involusi)."),
    ],
    "X": [  # XOR + operator Python + hukum Boolean (bos)
        ("Hasil dari 1 XOR 1 adalah?", ["0", "1", "2", "Error"], 0,
         "XOR = 1 hanya jika input BERBEDA; 1 dan 1 sama, jadi 0."),
        ("Gerbang XOR menghasilkan 1 jika...", ["Input berbeda", "Input sama", "Semua input 1", "Semua input 0"], 0,
         "XOR = 'exclusive or': 1 jika inputnya berbeda."),
        ("Operator XOR bitwise di Python adalah?", ["^", "&", "|", "~"], 0,
         "^ = XOR, & = AND, | = OR, ~ = NOT (bitwise)."),
        ("Di Python, 5 & 3 = ?", ["1", "3", "5", "7"], 0,
         "101 AND 011 = 001 = 1."),
        ("Di Python, 5 | 3 = ?", ["1", "3", "5", "7"], 3,
         "101 OR 011 = 111 = 7."),
        ("Hukum De Morgan: NOT(A AND B) sama dengan...",
         ["(NOT A) OR (NOT B)", "(NOT A) AND (NOT B)", "A OR B", "A AND B"], 0,
         "De Morgan: NOT(A AND B) = (NOT A) OR (NOT B)."),
        ("Menurut hukum komplemen, A OR (NOT A) = ?", ["0", "1", "A", "NOT A"], 1,
         "Salah satu dari A atau NOT A pasti 1, jadi hasilnya 1."),
        ("Menurut hukum identitas, A AND 0 = ?", ["0", "1", "A", "NOT A"], 0,
         "Apapun di-AND-kan dengan 0 hasilnya 0."),
    ],
}


# ---------------------------------------------------------------
# CLASS PERTANYAAN : satu soal pilihan ganda
# ---------------------------------------------------------------
class Pertanyaan:
    def __init__(self, teks, opsi, benar, penjelasan):
        self.teks = teks
        self.penjelasan = penjelasan
        # acak urutan pilihan, tapi catat letak jawaban benar yang baru
        urut = list(range(len(opsi)))
        random.shuffle(urut)
        self.opsi = [opsi[i] for i in urut]
        self.benar = urut.index(benar)

    def cek(self, pilihan):
        return pilihan == self.benar


# ---------------------------------------------------------------
# CLASS MONSTER : musuh dengan kumpulan soalnya sendiri
# ---------------------------------------------------------------
class Monster:
    DAFTAR = {   # kode: (nama, warna, HP, bos?)
        "A": ("Slime AND", (110, 200, 240), 3, False),
        "O": ("Goblin OR", (240, 160, 70), 3, False),
        "N": ("Ogre NOT", (170, 120, 220), 3, False),
        "X": ("RAJA XOR", (220, 60, 90), 5, True),
    }

    def __init__(self, kode, x, y):
        self.kode, self.x, self.y = kode, x, y
        self.nama, self.warna, self.hp_maks, self.bos = self.DAFTAR[kode]
        self.hp = self.hp_maks
        self.kalah = False

    def siapkan_soal(self):
        """Ambil soal milik monster ini dalam urutan acak."""
        soal = [Pertanyaan(*s) for s in DATA_SOAL[self.kode]]
        random.shuffle(soal)
        return soal

    def terluka(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kalah = True

    def pulihkan(self):
        self.hp = self.hp_maks

    def gambar(self, layar, font):
        px, py = self.x * KOTAK, self.y * KOTAK + PETA_Y
        r = KOTAK // 2 - (1 if self.bos else 3)
        pygame.draw.circle(layar, self.warna, (px + KOTAK // 2, py + KOTAK // 2), r)
        pygame.draw.circle(layar, HITAM, (px + KOTAK // 2, py + KOTAK // 2), r, 2)
        t = font.render(self.kode, True, HITAM)
        layar.blit(t, t.get_rect(center=(px + KOTAK // 2, py + KOTAK // 2)))


# ---------------------------------------------------------------
# CLASS PEMAIN : posisi, nyawa, level
# ---------------------------------------------------------------
class Pemain:
    def __init__(self, x, y):
        self.awal = (x, y)
        self.x, self.y = x, y
        self.hp_maks = 5
        self.hp = self.hp_maks
        self.level = 1

    def pindah(self, x, y):
        self.x, self.y = x, y

    def terluka(self):
        self.hp -= 1

    @property
    def mati(self):
        return self.hp <= 0

    def pulih(self):
        self.hp = self.hp_maks

    def naik_level(self):
        self.level += 1
        self.pulih()

    def kembali_ke_awal(self):
        self.x, self.y = self.awal
        self.pulih()

    def gambar(self, layar):
        px, py = self.x * KOTAK, self.y * KOTAK + PETA_Y
        pygame.draw.rect(layar, (70, 120, 230), (px + 3, py + 3, KOTAK - 6, KOTAK - 6), border_radius=8)
        for dx in (8, 17):   # mata
            pygame.draw.circle(layar, PUTIH, (px + dx, py + 12), 3)
            pygame.draw.circle(layar, HITAM, (px + dx, py + 12), 1)


# ---------------------------------------------------------------
# CLASS PETA : grid, tembok, dan posisi monster
# ---------------------------------------------------------------
class Peta:
    def __init__(self, data):
        self.tembok = set()
        self.monster = []
        self.awal = (1, 1)
        for y, baris in enumerate(data):
            for x, c in enumerate(baris):
                if c == "#":
                    self.tembok.add((x, y))
                elif c == "P":
                    self.awal = (x, y)
                elif c in Monster.DAFTAR:
                    self.monster.append(Monster(c, x, y))

    def bisa_jalan(self, x, y):
        return 0 <= x < KOLOM and 0 <= y < BARIS and (x, y) not in self.tembok

    def monster_di(self, x, y):
        for m in self.monster:
            if not m.kalah and (m.x, m.y) == (x, y):
                return m
        return None

    def sisa_monster_biasa(self):
        return sum(1 for m in self.monster if not m.bos and not m.kalah)

    def gambar(self, layar, font):
        for y in range(BARIS):
            for x in range(KOLOM):
                rect = (x * KOTAK, y * KOTAK + PETA_Y, KOTAK, KOTAK)
                if (x, y) in self.tembok:
                    pygame.draw.rect(layar, RUMPUT_1, rect)
                    cx, cy = x * KOTAK + KOTAK // 2, y * KOTAK + PETA_Y + KOTAK // 2
                    pygame.draw.rect(layar, BATANG, (cx - 3, cy + 4, 6, 9))
                    pygame.draw.circle(layar, POHON, (cx, cy - 2), 12)
                else:
                    pygame.draw.rect(layar, RUMPUT_1 if (x + y) % 2 == 0 else RUMPUT_2, rect)
        for m in self.monster:
            if not m.kalah:
                m.gambar(layar, font)


# ---------------------------------------------------------------
# CLASS GAME : mengatur state (intro / jelajah / battle / menang)
# ---------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.layar = pygame.display.set_mode((LEBAR, TINGGI), pygame.SCALED)
        pygame.display.set_caption("Petualangan Logika")
        self.jam = pygame.time.Clock()
        self.f_judul = pygame.font.SysFont(None, 42)
        self.f_sedang = pygame.font.SysFont(None, 28)
        self.f_kecil = pygame.font.SysFont(None, 23)

        # tombol panah di layar (untuk HP)
        self.dpad = {
            (0, -1): pygame.Rect(175, 430, 70, 70),
            (-1, 0): pygame.Rect(100, 505, 70, 70),
            (1, 0): pygame.Rect(250, 505, 70, 70),
            (0, 1): pygame.Rect(175, 580, 70, 70),
        }
        self.mulai_baru()

    def mulai_baru(self):
        self.peta = Peta(PETA)
        self.pemain = Pemain(*self.peta.awal)
        self.state = "intro"
        self.arah_tahan = None
        self.timer_jalan = 0
        self.pesan, self.pesan_timer = "", 0
        self.lawan = None

    # ---------------- BATTLE ----------------
    def mulai_battle(self, monster):
        self.lawan = monster
        self.antrian = monster.siapkan_soal()
        self.soal = self.antrian.pop()
        self.dipilih = None          # None = belum menjawab
        self.state = "battle"
        self.arah_tahan = None

    def jawab(self, i):
        if self.dipilih is not None:
            return
        self.dipilih = i
        if self.soal.cek(i):
            self.lawan.terluka()
        else:
            self.pemain.terluka()

    def lanjut_battle(self):
        """Dipanggil saat pemain mengetuk setelah melihat penjelasan."""
        if self.lawan.kalah:
            self.menangkan_battle()
        elif self.pemain.mati:
            self.kalahkan_pemain()
        else:
            if not self.antrian:                      # soal habis -> kocok ulang
                self.antrian = self.lawan.siapkan_soal()
            self.soal = self.antrian.pop()
            self.dipilih = None

    def menangkan_battle(self):
        bos = self.lawan.bos
        self.pemain.naik_level()
        self.state = "menang" if bos else "jelajah"
        if not bos:
            self.toast(f"{self.lawan.nama} kalah! Naik ke Level {self.pemain.level}")

    def kalahkan_pemain(self):
        self.lawan.pulihkan()
        self.pemain.kembali_ke_awal()
        self.state = "jelajah"
        self.toast("Kamu kalah... belajar lagi lalu coba lagi!")

    # ---------------- JELAJAH ----------------
    def toast(self, teks):
        self.pesan, self.pesan_timer = teks, 2500

    def langkah(self, arah):
        nx, ny = self.pemain.x + arah[0], self.pemain.y + arah[1]
        if not self.peta.bisa_jalan(nx, ny):
            return
        m = self.peta.monster_di(nx, ny)
        if m:
            if m.bos and self.peta.sisa_monster_biasa() > 0:
                self.toast("Kalahkan 3 monster lain dulu!")
                return
            self.mulai_battle(m)
            return
        self.pemain.pindah(nx, ny)

    # ---------------- INPUT ----------------
    def proses_input(self):
        peta_tombol = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
                       pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
                       pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
                       pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if self.state == "jelajah" and e.key in peta_tombol:
                    self.langkah(peta_tombol[e.key])
                elif self.state == "battle" and pygame.K_1 <= e.key <= pygame.K_4:
                    self.jawab(e.key - pygame.K_1)
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.ketuk(None)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.ketuk(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP:
                self.arah_tahan = None
        return True

    def rect_pilihan(self, i):
        return pygame.Rect(20, 300 + i * 66, 380, 56)

    def ketuk(self, pos):
        if self.state == "intro":
            self.state = "jelajah"
        elif self.state == "menang":
            self.mulai_baru()
        elif self.state == "jelajah" and pos:
            for arah, rect in self.dpad.items():
                if rect.collidepoint(pos):
                    self.langkah(arah)
                    self.arah_tahan = arah
                    self.timer_jalan = -150     # jeda sebelum auto-ulang
        elif self.state == "battle":
            if self.dipilih is not None:
                self.lanjut_battle()
            elif pos:
                for i in range(len(self.soal.opsi)):
                    if self.rect_pilihan(i).collidepoint(pos):
                        self.jawab(i)

    # ---------------- UPDATE ----------------
    def update(self, dt):
        if self.pesan_timer > 0:
            self.pesan_timer -= dt
        if self.state == "jelajah" and self.arah_tahan:
            self.timer_jalan += dt
            if self.timer_jalan >= JEDA_JALAN:
                self.timer_jalan = 0
                self.langkah(self.arah_tahan)

    # ---------------- GAMBAR ----------------
    def teks(self, s, font, pos, warna=PUTIH, tengah=False):
        g = font.render(s, True, warna)
        self.layar.blit(g, g.get_rect(center=pos) if tengah else g.get_rect(topleft=pos))

    def paragraf(self, s, font, x, y, lebar, warna=PUTIH, tengah=False, jarak=4):
        """Tulis teks panjang dengan pemotongan baris otomatis."""
        baris, sekarang = [], ""
        for kata in s.split():
            coba = (sekarang + " " + kata).strip()
            if font.size(coba)[0] <= lebar:
                sekarang = coba
            else:
                baris.append(sekarang)
                sekarang = kata
        baris.append(sekarang)
        for b in baris:
            g = font.render(b, True, warna)
            self.layar.blit(g, g.get_rect(midtop=(x + lebar // 2, y)) if tengah else (x, y))
            y += g.get_height() + jarak
        return y

    def bar_hp(self, x, y, lebar, hp, hp_maks, warna):
        pygame.draw.rect(self.layar, HITAM, (x, y, lebar, 14), border_radius=6)
        isi = max(0, int(lebar * hp / hp_maks))
        if isi:
            pygame.draw.rect(self.layar, warna, (x, y, isi, 14), border_radius=6)

    def gambar_header(self):
        pygame.draw.rect(self.layar, PANEL, (0, 0, LEBAR, HEADER))
        self.teks(f"Lv {self.pemain.level}", self.f_sedang, (12, 8), EMAS)
        self.teks("HP", self.f_kecil, (12, 30))
        self.bar_hp(38, 31, 120, self.pemain.hp, self.pemain.hp_maks, HIJAU)
        sisa = self.peta.sisa_monster_biasa()
        info = "Bos terbuka!" if sisa == 0 else f"Monster tersisa: {sisa}"
        self.teks(info, self.f_kecil, (LEBAR - 12 - self.f_kecil.size(info)[0], 18))

    def gambar(self):
        self.layar.fill(BG)
        if self.state == "intro":
            self.gambar_intro()
        elif self.state == "battle":
            self.gambar_header()
            self.gambar_battle()
        elif self.state == "menang":
            self.gambar_menang()
        else:
            self.gambar_header()
            self.peta.gambar(self.layar, self.f_kecil)
            self.pemain.gambar(self.layar)
            self.gambar_dpad()
            if self.pesan_timer > 0:
                self.paragraf(self.pesan, self.f_sedang, 20, 424, 380, EMAS, True)
        pygame.display.flip()

    def gambar_dpad(self):
        for arah, r in self.dpad.items():
            pygame.draw.rect(self.layar, TOMBOL_AKTIF if arah == self.arah_tahan else TOMBOL, r, border_radius=14)
            cx, cy = r.center
            dx, dy = arah
            titik = [(cx + dx * 18, cy + dy * 18),
                     (cx - dx * 10 - dy * 14, cy - dy * 10 + dx * 14),
                     (cx - dx * 10 + dy * 14, cy - dy * 10 - dx * 14)]
            pygame.draw.polygon(self.layar, PUTIH, titik)

    def gambar_intro(self):
        self.teks("PETUALANGAN", self.f_judul, (LEBAR // 2, 150), EMAS, True)
        self.teks("LOGIKA", self.f_judul, (LEBAR // 2, 195), EMAS, True)
        y = self.paragraf("Kamu Pahlawan Logika! Kalahkan Slime AND, Goblin OR, dan Ogre NOT, "
                          "lalu hadapi RAJA XOR.", self.f_sedang, 30, 260, 360, PUTIH, True)
        y = self.paragraf("Sentuh monster untuk bertarung. Jawab soal dengan benar untuk melukai "
                          "monster. Jawab salah, nyawamu berkurang.", self.f_kecil, 30, y + 14, 360, (200, 205, 230), True)
        self.teks("Ketuk layar untuk mulai", self.f_sedang, (LEBAR // 2, 520), HIJAU, True)

    def gambar_battle(self):
        m = self.lawan
        # kartu monster
        pygame.draw.rect(self.layar, PANEL, (20, 62, 380, 76), border_radius=12)
        pygame.draw.circle(self.layar, m.warna, (62, 100), 26)
        pygame.draw.circle(self.layar, HITAM, (62, 100), 26, 3)
        self.teks(m.kode, self.f_sedang, (62, 100), HITAM, True)
        self.teks(m.nama, self.f_sedang, (105, 78))
        self.bar_hp(105, 108, 270, m.hp, m.hp_maks, MERAH)
        # soal
        pygame.draw.rect(self.layar, PANEL, (20, 150, 380, 135), border_radius=12)
        self.paragraf(self.soal.teks, self.f_sedang, 34, 170, 352, PUTIH, True)
        # pilihan
        for i, o in enumerate(self.soal.opsi):
            r = self.rect_pilihan(i)
            warna = TOMBOL
            if self.dipilih is not None:
                if i == self.soal.benar:
                    warna = (60, 160, 90)
                elif i == self.dipilih:
                    warna = (190, 60, 70)
            pygame.draw.rect(self.layar, warna, r, border_radius=12)
            self.paragraf(f"{i + 1}. {o}", self.f_sedang, r.x + 12, r.y + 16, r.width - 24, PUTIH, False)
        # umpan balik + penjelasan
        if self.dipilih is not None:
            benar = self.soal.cek(self.dipilih)
            self.teks("BENAR! Monster terluka" if benar else "SALAH! Kamu terluka",
                      self.f_sedang, (LEBAR // 2, 574), HIJAU if benar else MERAH, True)
            self.paragraf(self.soal.penjelasan, self.f_kecil, 30, 594, 360, (220, 225, 245), True)
            self.teks("Ketuk untuk lanjut", self.f_kecil, (LEBAR // 2, 645), EMAS, True)

    def gambar_menang(self):
        self.teks("SELAMAT!", self.f_judul, (LEBAR // 2, 190), EMAS, True)
        self.paragraf("Raja XOR sudah kalah. Kamu resmi jadi Master Logika Boolean!",
                      self.f_sedang, 30, 250, 360, PUTIH, True)
        self.teks(f"Level akhir: {self.pemain.level}", self.f_sedang, (LEBAR // 2, 380), HIJAU, True)
        self.teks("Ketuk untuk main lagi", self.f_sedang, (LEBAR // 2, 480), EMAS, True)

    # ---------------- LOOP UTAMA ----------------
    async def jalankan(self):
        jalan = True
        while jalan:
            dt = self.jam.tick(FPS)
            jalan = self.proses_input()
            self.update(dt)
            self.gambar()
            await asyncio.sleep(0)      # wajib untuk pygbag
        pygame.quit()


async def main():
    await Game().jalankan()


asyncio.run(main())
