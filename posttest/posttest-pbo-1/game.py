from main import Card, Player

def buat_pemain():
    card1 = Card(name="Fire Breath", effect="Membakar Musuh", damage=100, sp_cost=10, card_type=1)
    card2 = Card(name="Water Blessing", effect="Menenggelamkan Musuh", damage=90, sp_cost=0, card_type=2)
    card3 = Card(name="Plant Sprout", effect="Mengikat Musuh", damage=50, sp_cost=15, card_type=3)

    pemain1 = Player(name="Warrior", health=100, mana=90, level=5, list_card=[card1, card2])
    pemain2 = Player(name="Novice", health=250, mana=80, level=2, list_card=[card2, card3, card1])
    return pemain1, pemain2


def tampilkan_kartu(pemain):
    kartu = pemain.list_card
    if not kartu:
        print("  (Hand kosong)")
        return

    for nomor, k in enumerate(kartu, start=1):
        print(f"  [{nomor}] {k.name} ({k.card_type}) - Damage: {k.damage}, SP: {k.sp_cost}")


def tampilkan_status(pemain):
    print(f"\n--- Status {pemain.name} (Level {pemain.level}) ---")
    print(f"Health : {pemain.health}")
    print(f"Mana   : {pemain.mana}")
    print(f"Hand   : {len(pemain.list_card)}/{pemain.checkMaximumHand()} kartu")
    tampilkan_kartu(pemain)


def aksi_pakai_kartu(pemain, lawan):
    if not pemain.list_card:
        print("Hand kosong, tidak ada kartu yang bisa dipakai!")
        return False

    tampilkan_kartu(pemain)
    pilihan = input("Pilih nomor kartu (0 = batal): ").strip()

    try:
        nomor = int(pilihan)
    except ValueError:
        print("Input harus berupa angka!")
        return False

    if nomor == 0:
        return False
    if not 1 <= nomor <= len(pemain.list_card):
        print("Nomor kartu tidak valid!")
        return False

    kartu = pemain.list_card[nomor - 1]
    if pemain.mana < kartu.sp_cost:
        print(f"Mana tidak cukup! {kartu.name} butuh {kartu.sp_cost} SP, mana kamu {pemain.mana}.")
        return False

    pemain.use_card(nomor, lawan)
    pemain.reduce_mana = kartu.sp_cost
    print(f"Sisa mana {pemain.name}: {pemain.mana}")
    return True


def aksi_tarik_kartu(pemain):
    jumlah_sebelum = len(pemain.list_card)
    pemain.draw_card()
    return len(pemain.list_card) > jumlah_sebelum


def game_loop():
    pemain1, pemain2 = buat_pemain()
    daftar_pemain = [pemain1, pemain2]

    print("=" * 45)
    print("        CARD GAME SEDERHANA")
    print("=" * 45)
    tampilkan_status(pemain1)
    tampilkan_status(pemain2)

    giliran = 0
    while pemain1.is_alive and pemain2.is_alive:
        aktif = daftar_pemain[giliran % 2]
        lawan = daftar_pemain[(giliran + 1) % 2]

        print("\n" + "=" * 45)
        print(f"Ronde {giliran // 2 + 1} - Giliran {aktif.name}")
        print(f"Health {aktif.name}: {aktif.health} | Health {lawan.name}: {lawan.health}")

        giliran_selesai = False
        while not giliran_selesai:
            print("\n[1] Pakai kartu   [2] Tarik kartu   [3] Lihat status")
            print("[4] Lewati giliran   [0] Keluar")
            pilihan = input("Pilih aksi: ").strip()

            if pilihan == "1":
                giliran_selesai = aksi_pakai_kartu(aktif, lawan)
            elif pilihan == "2":
                giliran_selesai = aksi_tarik_kartu(aktif)
            elif pilihan == "3":
                tampilkan_status(aktif)
            elif pilihan == "4":
                print(f"{aktif.name} melewati giliran.")
                giliran_selesai = True
            elif pilihan == "0":
                print("Permainan dihentikan.")
                return
            else:
                print("Pilihan tidak dikenal, coba lagi.")

        giliran += 1

    pemenang = pemain1 if pemain1.is_alive else pemain2
    print("\n" + "=" * 45)
    print(f"{pemenang.name} MENANG!")
    exp = Player.calculateExpGain(pemenang.level)     # staticmethod
    print(f"{pemenang.name} mendapatkan {exp:.1f} EXP")
    print("=" * 45)


if __name__ == "__main__":
    try:
        game_loop()
    except (EOFError, KeyboardInterrupt):
        print("\nPermainan dihentikan.")