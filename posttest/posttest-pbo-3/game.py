"""Entry point dan alur utama game roguelike berbasis CLI."""
import random

from main import Player, Battle, Shop, create_enemy, demonstrate_oop, clear

def show_main_menu():
    clear()
    print("=" * 48)
    print("CARD GAME SEDERHANA")
    print("=" * 48)
    print("[1] Mulai Run")
    print("[2] Lihat aturan singkat")
    # print("[3] Demonstrasi OOP")
    print("[0] Keluar")
    print("-" * 48)


def show_rules():
    clear()
    print("=" * 90)
    print("ATURAN SINGKAT")
    print("=" * 90)
    print("""- Kalahkan seluruh musuh untuk memperoleh gold dan maju ke ronde berikutnya
- HP mencapai 0 berarti run berakhir
- Kartu fisik menggunakan HP, sedangkan kartu elemental/support menggunakan MP
- Setelah menang, shop menyediakan kartu baru dan upgrade stat karakter""")
    print("-" * 90)
    input("Tekan Enter untuk melanjutkan...")


def run_game():
    player = Player()
    round_number = 1
    highscore = 0

    while player.is_alive:
        enemy_count = random.randint(1, min(3, 1 + round_number // 2))
        enemies = [create_enemy(round_number, i + 1) for i in range(enemy_count)]
        battle = Battle(player, enemies, round_number)
        won = battle.run()
        if not won:
            break

        player.gold += sum(enemy.gold_reward for enemy in enemies)
        highscore = round_number
        print(f"\nRonde {round_number} selesai! Gold sekarang: {player.gold}.")
        Shop(player, round_number).visit()
        player.restore_hp(10)
        player.restore_mp(8)
        round_number += 1

    print("\n" + "=" * 48)
    print("                 GAME OVER")
    print(f"Ronde tertinggi yang dilewati: {highscore}")
    print(f"Gold tersisa: {player.gold}")
    print("=" * 48)
    return highscore


def main():
    highscore = 0
    while True:
        show_main_menu()
        choice = input("Pilih menu: ").strip()
        if choice == "1":
            highscore = max(highscore, run_game())
        elif choice == "2":
            show_rules()
        elif choice == "3":
            demonstrate_oop()
        elif choice == "0":
            print(f"Terima kasih bermain! Highscore sesi ini: {highscore}")
            break
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPermainan dihentikan.")
