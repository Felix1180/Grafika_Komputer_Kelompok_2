import pygame
import pygame_gui
import sys
import random
import os

import time

# Inisialisasi Pygame
pygame.init()

# Setup layar
WIDTH, HEIGHT = 800, 500
LAYAR = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mesin Slot")

# Warna
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
# Warna tombol aktif dan non-aktif
WARNA_TOMBOL_AKTIF = (255, 255, 255)
WARNA_TOMBOL_NON_AKTIF = (255, 255, 255)

# Inisialisasi posisi, kecepatan, dan percepatan simbol
jumlah_simbol = 5
jarak_antar_simbol = 100
posisi_simbol_tengah = [i * jarak_antar_simbol for i in range(jumlah_simbol)]  # Posisi awal simbol di gulungan tengah
posisi_simbol_kiri = [pos for pos in posisi_simbol_tengah]  # Posisi awal simbol di gulungan kiri
posisi_simbol_kanan = [pos for pos in posisi_simbol_tengah]  # Posisi awal simbol di gulungan kanan
saldo_awal_pemain = 0
saldo_pemain = saldo_awal_pemain
bet = 1

total_win = 0

initial = True
kecepatan_simbol_kiri = 18 # Contoh kecepatan putaran simbol
kecepatan_simbol_tengah =18 # Contoh kecepatan putaran simbol
kecepatan_simbol_kanan = 18 # Contoh kecepatan putaran simbol
percepatan_perlambatan = 0.04  # Contoh percepatan perlambatan

ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path="theme.json")

# Daftar simbol untuk setiap gulungan
daftar_simbol_murah_tengah = [pygame.image.load(os.path.join("simbol", "simbol_murah_{}.png".format(i))) for i in
                              range(5)]
daftar_simbol_murah_kiri = [pygame.image.load(os.path.join("simbol", "simbol_murah_{}.png".format(i))) for i in
                            range(5)]
daftar_simbol_murah_kanan = [pygame.image.load(os.path.join("simbol", "simbol_murah_{}.png".format(i))) for i in
                             range(5)]

daftar_simbol_mahal_tengah = [pygame.image.load(os.path.join("simbol", "simbol_mahal_{}.png".format(i))) for i in
                              range(5)]
daftar_simbol_mahal_kiri = [pygame.image.load(os.path.join("simbol", "simbol_mahal_{}.png".format(i))) for i in
                            range(5)]
daftar_simbol_mahal_kanan = [pygame.image.load(os.path.join("simbol", "simbol_mahal_{}.png".format(i))) for i in
                             range(5)]

if saldo_awal_pemain >= 5:
    daftar_simbol_kiri= daftar_simbol_murah_kiri.copy()
    daftar_simbol_tengah = daftar_simbol_murah_tengah.copy()
    daftar_simbol_kanan = daftar_simbol_murah_kanan.copy()
else:
    daftar_simbol_kiri = daftar_simbol_mahal_kiri.copy()
    daftar_simbol_tengah = daftar_simbol_mahal_tengah.copy()
    daftar_simbol_kanan = daftar_simbol_mahal_kanan.copy()

# Mengacak simbol awal
random.shuffle(daftar_simbol_tengah)
random.shuffle(daftar_simbol_kiri)
random.shuffle(daftar_simbol_kanan)
random.shuffle(daftar_simbol_tengah)
random.shuffle(daftar_simbol_kiri)
random.shuffle(daftar_simbol_kanan)

def process_input(input_text, min_value, max_value, default_value):
    try:
        if input_text.strip() == "":
            return default_value
        else:
            value = float(input_text)
            if min_value <= value <= max_value:
                return value
            else:
                return default_value
    except ValueError:
        return default_value

def draw_line_dda(surface, color, start, end, lebar=1):
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    x_increment = dx / steps
    y_increment = dy / steps
    x = x1
    y = y1
    for _ in range(steps + 1):
        pygame.draw.circle(surface, color, (int(x), int(y)), lebar)
        x += x_increment
        y += y_increment

def draw_rounded_rect(surface, color, rect, rounded_corners, lebar):
    x, y, width, height = rect
    radius = rounded_corners

    # Garis atas
    draw_line_dda(surface, color, (x + radius, y), (x + width - radius, y), lebar)
    # Garis kanan
    draw_line_dda(surface, color, (x + width, y + radius), (x + width, y + height - radius), lebar)
    # Garis bawah
    draw_line_dda(surface, color, (x + width - radius, y + height), (x + radius, y + height),lebar)
    # Garis kiri
    draw_line_dda(surface, color, (x, y + height - radius), (x, y + radius),lebar)

    # Lingkaran sudut kiri atas
    draw_arc(surface, color, (x + radius, y + radius), radius, 180, 270, int(lebar + (9/10 * lebar)))
    # Lingkaran sudut kanan atas
    draw_arc(surface, color, (x + width - radius, y + radius), radius, 270, 360,int(lebar + (9/10 * lebar)))
    # Lingkaran sudut kanan bawah
    draw_arc(surface, color, (x + width - radius, y + height - radius), radius, 0, 90, int(lebar + (9/10 * lebar)))
    # Lingkaran sudut kiri bawah
    draw_arc(surface, color, (x + radius, y + height - radius), radius, 90, 180, int(lebar + (9/10 * lebar)))

def draw_rect_dda(surface, color, rect, width=1):
    x, y, width_rect, height = rect
    draw_line_dda(  surface, color, (x, y), (x + width_rect, y), width)
    draw_line_dda(surface, color, (x + width_rect, y), (x + width_rect, y + height), width)
    draw_line_dda(surface, color, (x + width_rect, y + height), (x, y + height), width)
    draw_line_dda(surface, color, (x, y + height), (x, y), width)

def draw_rect_scanline(surface, color, rect):
    x, y, width, height = rect
    for y_coord in range(y, y + height,10):
        draw_line_dda(surface, color, (x, y_coord), (x + width, y_coord),10)

def draw_arc(surface, color, center, radius, start_angle, end_angle, lebar, num_segments=30):
    cx, cy = center
    vertices = []
    for i in range(num_segments):
        angle = start_angle + (end_angle - start_angle) * i / num_segments
        x = cx + radius * pygame.math.Vector2(1, 0).rotate(angle)[0]
        y = cy + radius * pygame.math.Vector2(1, 0).rotate(angle)[1]
        vertices.append((int(x), int(y)))
    for i in range(len(vertices) - 1):
        pygame.draw.line(surface, color, vertices[i], vertices[i + 1], lebar)

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def draw_filled_rounded_rect(surface, color, colorfill, rect, rounded_corners, lebar):
    draw_rect_scanline(LAYAR, colorfill, rect)
    # Draw the rounded rectangle
    draw_rounded_rect(surface, color, rect, rounded_corners, lebar)


def gambar_mesin():
    #Kepala
    draw_rect_scanline(LAYAR, (204, 0, 0), (252, 0, 290, 97))
    draw_rect_dda(LAYAR, (0,0,0),(240,0,313,97),3)
    #Mesin Besar
    draw_rect_dda(LAYAR, (0,0,0),(250,313,293,220), 3)
    #Grid Utama
    draw_rounded_rect(LAYAR, (0, 0, 0), (262,97,265,214), 40,3)
    #Penutup Ilusi
    draw_rect_scanline(LAYAR, (255, 255, 255), (265, 325, 260, 5))
    #Container Lingkaran
    draw_rect_scanline(LAYAR, (255, 215, 0), (252, 340, 293, 70))
    draw_rect_dda(LAYAR, (0,0,0),(241,330,313,79),3)

    for y in range (12,100,10):
        draw_line_dda(LAYAR, (255, 255, 255), (265, y+409), (530, y+409), 9)

    #Lobang Koin
    draw_filled_rounded_rect((LAYAR), (0,0,0), (255,255,255), (360,440,73,37), 5, 2)
    #Garis mesin
    draw_line_dda(LAYAR,(0,0,0), (345,97),(345,311),2)
    draw_line_dda(LAYAR, (0, 0, 0), (442, 97), (442, 311), 2)

    draw_line_dda(LAYAR, (0, 0, 0), (250, 98), (250, 320), 3)
    draw_line_dda(LAYAR, (0, 0, 0), (543, 98), (543, 320), 3)

    # Tampilkan saldo pemain
    font = pygame.font.Font(None, 28)  # Ukuran dan jenis font teks
    teks_saldo = font.render(f"Credit: {saldo_pemain}", True, HITAM)  # Render teks saldo
    LAYAR.blit(teks_saldo, (265, 360))  # Gambar teks saldo pada layar

    # Tampilkan saldo pemain
    font = pygame.font.Font(None, 36)  # Ukuran dan jenis font teks
    teks_win = font.render(f"Total win: {total_win}", True, PUTIH)  # Render teks saldo
    LAYAR.blit(teks_win, (320, 40))

    font = pygame.font.Font(None, 28)  # Ukuran dan jenis font teks
    teks_win = font.render("x", True, HITAM)  # Render teks saldo
    LAYAR.blit(teks_win, (440, 350))


    font = pygame.font.Font(None, 28)  # Ukuran dan jenis font teks
    teks_win = font.render("coin", True, HITAM)  # Render teks saldo
    LAYAR.blit(teks_win, (480, 350))


def gambar_ulang_layar():
    LAYAR.fill(PUTIH)  # Bersihkan layar dengan warna putih
    # Gambar simbol pada posisi yang baru di gulungan tengah
    for i, posisi in enumerate(posisi_simbol_tengah):
        LAYAR.blit(simbol_tengah[i], (WIDTH // 2 - 30, posisi - 30))

    # Gambar simbol pada posisi yang baru di gulungan kiri
    for i, posisi in enumerate(posisi_simbol_kiri):
        LAYAR.blit(simbol_kiri[i], (WIDTH // 2 - jarak_antar_simbol - 30, posisi - 30))

    # Gambar simbol pada posisi yang baru di gulungan kanan
    for i, posisi in enumerate(posisi_simbol_kanan):
        LAYAR.blit(simbol_kanan[i], (WIDTH // 2 + jarak_antar_simbol - 30, posisi - 30))

    # Gambar tombol dengan status yang sesuai
    if not gulungan_berputar_tengah:
        pygame.draw.rect(LAYAR, WARNA_TOMBOL_AKTIF, tombol_start_tengah)
    else:
        pygame.draw.rect(LAYAR, WARNA_TOMBOL_NON_AKTIF, tombol_start_tengah)
def tuas():
    # Dasar Tuas
    draw_rect_dda(LAYAR, (0, 0, 0), (543, 161, 30, 80), 3)
    draw_rounded_rect(LAYAR, (0, 0, 0), (573, 190, 20, 20), 5, 3)

    # Gambar tombol dengan status yang sesuai
    if not gulungan_berputar_tengah:
        draw_line_dda(LAYAR, (0, 0, 0), (593, 195), (610, 80), 3)
        pygame.draw.circle(LAYAR, (0, 0, 0), (610, 80), 10)
    else:
        draw_line_dda(LAYAR, (0, 0, 0), (593, 195), (610, 300), 3)
        pygame.draw.circle(LAYAR, (0, 0, 0), (610, 300), 10)

def cek_menang():
    global saldo_pemain, total_win
    # Mendapatkan nama file simbol pada ketinggian 200 (index 2) pada tiap gulungan
    ukuran_simbol_kiri = daftar_simbol_kiri[2].get_size()
    ukuran_simbol_tengah = daftar_simbol_tengah[2].get_size()
    ukuran_simbol_kanan = daftar_simbol_kanan[2].get_size()

    if ukuran_simbol_kiri == (50, 50) == ukuran_simbol_tengah == ukuran_simbol_kanan:
        saldo_pemain += 10 * bet
        total_win += 10 * bet
        print("JACKPOT")
    elif ukuran_simbol_kiri == (51, 51) == ukuran_simbol_tengah == ukuran_simbol_kanan:
        saldo_pemain += 2 * bet
        total_win += 2 * bet
        print("LEMON")
    elif ukuran_simbol_kiri == (52, 52) == ukuran_simbol_tengah == ukuran_simbol_kanan:
        saldo_pemain += 3 * bet
        total_win += 3 * bet
        print("DIAMOND")
    elif ukuran_simbol_kiri == (50, 50) == ukuran_simbol_tengah:
        saldo_pemain += 2 * bet
        total_win += 2 * bet
        print("2 77")
    elif ukuran_simbol_kiri == (51, 51) == ukuran_simbol_tengah:
        saldo_pemain += 1 * bet
        total_win += 1 * bet
        print("2 Lemon")
    elif ukuran_simbol_kiri == (52, 52) == ukuran_simbol_tengah:
        saldo_pemain += 1 * bet
        total_win += 1 * bet
        print("2 Diamond")


# Inisialisasi tombol start
tombol_start_tengah = pygame.Rect(593, 65, 30, 30)

# Perulangan utama permainan
running = True
clock = pygame.time.Clock()
gulungan_berputar_kiri = False  # Menyimpan status apakah gulungan kiri sedang berputar atau tidak
waktu_mulai_putaran_kiri = 0

gulungan_berputar_tengah = False  # Menyimpan status apakah gulungan tengah sedang berputar atau tidak
waktu_mulai_putaran_tengah = 0

gulungan_berputar_kanan = False  # Menyimpan status apakah gulungan kanan sedang berputar atau tidak
waktu_mulai_putaran_kanan = 0

# Jeda antara putaran gulungan kiri dan tengah (dalam detik)
jeda_kiri_tengah = 0.15
# Jeda antara putaran gulungan tengah dan kanan (dalam detik)
jeda_tengah_kanan = 0.2

bet_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(430, 370, 35, 20),
    manager=ui_manager,
)
coin_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(480, 370, 35, 20),
    manager=ui_manager,
)


while running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if not gulungan_berputar_tengah and tombol_start_tengah.collidepoint(event.pos) and bet<= saldo_pemain:
                bet_input.disable()
                saldo_pemain -= bet
                if kecepatan_simbol_kiri <= 0:  # Gulungan kiri telah berhenti
                    # Reset posisi simbol
                    posisi_simbol_kiri = [i * jarak_antar_simbol for i in range(jumlah_simbol)]
                    # Reset kecepatan dan status awal
                    kecepatan_simbol_kiri = 18
                    initial = True
                # Mulai berputar kembali
                gulungan_berputar_kiri = True
                waktu_mulai_putaran_kiri = pygame.time.get_ticks() / 1000

                # Set waktu mulai putaran untuk gulungan tengah
                waktu_mulai_putaran_tengah = waktu_mulai_putaran_kiri + jeda_kiri_tengah

                # Set waktu mulai putaran untuk gulungan kanan
                waktu_mulai_putaran_kanan = waktu_mulai_putaran_tengah + jeda_tengah_kanan

                if kecepatan_simbol_tengah <= 0:  # Gulungan tengah telah berhenti
                    # Reset posisi simbol
                    posisi_simbol_tengah = [i * jarak_antar_simbol for i in range(jumlah_simbol)]
                    # Reset kecepatan dan status awal
                    kecepatan_simbol_tengah = 18
                    initial = True
                # Mulai berputar kembali
                gulungan_berputar_tengah = True

                if kecepatan_simbol_kanan <= 0:  # Gulungan kanan telah berhenti
                    # Reset posisi simbol
                    posisi_simbol_kanan = [i * jarak_antar_simbol for i in range(jumlah_simbol)]
                    # Reset kecepatan dan status awal
                    kecepatan_simbol_kanan = 18
                    initial = True
                # Mulai berputar kembali
                gulungan_berputar_kanan = True

        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == bet_input:
                    bet = process_input(event.text, 1, 5, 1)
                    bet_input.set_text(str(bet))
                if event.ui_element == coin_input:
                    saldo_pemain += process_input(event.text, 1, 100, 1)
                    coin_input.set_text(str(saldo_pemain))

        ui_manager.process_events(event)

    # Logika perputaran untuk gulungan kiri
    if gulungan_berputar_kiri:
        # Hitung delta waktu
        waktu_sekarang = pygame.time.get_ticks() / 1000
        delta_waktu = waktu_sekarang - waktu_mulai_putaran_kiri

        # Hitung posisi baru simbol berdasarkan waktu yang berlalu dengan GLBB
        for i in range(len(posisi_simbol_kiri)):
            # Rumus GLBB: s = s0 + v0*t + 0.5*a*t^2
            posisi_simbol_kiri[
                i] += kecepatan_simbol_kiri * delta_waktu + 0.5 * percepatan_perlambatan * delta_waktu ** 2

        # Hapus simbol yang mencapai koordinat y = 600 dan tambahkan simbol baru di atas
        if posisi_simbol_kiri[-1] >= HEIGHT:
            posisi_simbol_kiri.pop(-1)
            # Memilih simbol baru secara acak dari daftar yang sesuai
            if saldo_pemain < 3:
                simbol_baru = random.choice(daftar_simbol_mahal_kiri)
            elif saldo_pemain >= 3:
                simbol_baru = random.choice(daftar_simbol_murah_kiri)
            posisi_simbol_kiri.insert(0, posisi_simbol_kiri[0] - jarak_antar_simbol)
            daftar_simbol_kiri.insert(0, simbol_baru)

        # Perbarui kecepatan (perlambatan)
        kecepatan_simbol_kiri -= percepatan_perlambatan * delta_waktu

        # Cek apakah gulungan telah berhenti berputar
        if kecepatan_simbol_kiri <= 0:
            gulungan_berputar_kiri = False

    # Logika perputaran untuk gulungan tengah
    if gulungan_berputar_tengah:
        # Hitung delta waktu
        waktu_sekarang = pygame.time.get_ticks() / 1000
        delta_waktu = waktu_sekarang - waktu_mulai_putaran_tengah
        if delta_waktu >= 0:
            # Hitung posisi baru simbol berdasarkan waktu yang berlalu dengan GLBB
            for i in range(len(posisi_simbol_tengah)):
                # Rumus GLBB: s = s0 + v0*t + 0.5*a*t^2
                posisi_simbol_tengah[
                    i] += kecepatan_simbol_tengah * delta_waktu + 0.5 * percepatan_perlambatan * delta_waktu ** 2

            # Hapus simbol yang mencapai koordinat y = 600 dan tambahkan simbol baru di atas
            if posisi_simbol_tengah[-1] >= HEIGHT:
                posisi_simbol_tengah.pop(-1)
                # Memilih simbol baru secara acak dari daftar yang sesuai
                if saldo_pemain < 3:
                    simbol_baru = random.choice(daftar_simbol_mahal_tengah)
                elif saldo_pemain >= 3:
                    simbol_baru = random.choice(daftar_simbol_murah_tengah)
                posisi_simbol_tengah.insert(0, posisi_simbol_tengah[0] - jarak_antar_simbol)
                daftar_simbol_tengah.insert(0, simbol_baru)

            # Perbarui kecepatan (perlambatan)
            kecepatan_simbol_tengah -= percepatan_perlambatan * delta_waktu

            # Cek apakah gulungan telah berhenti berputar
            if kecepatan_simbol_tengah <= 0:
                gulungan_berputar_tengah = False

    # Logika perputaran untuk gulungan kanan
    if gulungan_berputar_kanan:
        # Hitung delta waktu
        waktu_sekarang = pygame.time.get_ticks() / 1000
        delta_waktu = waktu_sekarang - waktu_mulai_putaran_kanan
        if delta_waktu >= 0:
            # Hitung posisi baru simbol berdasarkan waktu yang berlalu dengan GLBB
            for i in range(len(posisi_simbol_kanan)):
                # Rumus GLBB: s = s0 + v0*t + 0.5*a*t^2
                posisi_simbol_kanan[
                    i] += kecepatan_simbol_kanan * delta_waktu + 0.5 * percepatan_perlambatan * delta_waktu ** 2

            # Hapus simbol yang mencapai koordinat y = 600 dan tambahkan simbol baru di atas
            if posisi_simbol_kanan[-1] >= HEIGHT:
                posisi_simbol_kanan.pop(-1)
                # Memilih simbol baru secara acak dari daftar yang sesuai
                if saldo_pemain < 3:
                    simbol_baru = random.choice(daftar_simbol_mahal_kanan)
                elif saldo_pemain >= 3:
                    simbol_baru = random.choice(daftar_simbol_murah_kanan)
                posisi_simbol_kanan.insert(0, posisi_simbol_kanan[0] - jarak_antar_simbol)  
                daftar_simbol_kanan.insert(0, simbol_baru)

            # Perbarui kecepatan (perlambatan)
            kecepatan_simbol_kanan -= percepatan_perlambatan * delta_waktu

            # Cek apakah gulungan telah berhenti berputar
            if kecepatan_simbol_kanan <= 0:
                gulungan_berputar_kanan = False
                bet_input.enable()
                cek_menang()


    # Simpan gambar simbol untuk digunakan di dalam fungsi gambar_ulang_layar
    simbol_tengah = [daftar_simbol_tengah[i] for i in range(len(posisi_simbol_tengah))]
    simbol_kiri = [daftar_simbol_kiri[i] for i in range(len(posisi_simbol_kiri))]
    simbol_kanan = [daftar_simbol_kanan[i] for i in range(len(posisi_simbol_kanan))]

    # Gambar ulang layar dengan posisi simbol yang baru

    gambar_ulang_layar()
    gambar_mesin()
    tuas()
    ui_manager.update(time_delta)
    ui_manager.draw_ui(LAYAR)
    pygame.display.flip()  # Perbarui tampilan


    # Batasi frame rate
    clock.tick(60)

pygame.quit()
sys.exit()