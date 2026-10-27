# Echoes of the Deck — Posttest 3 PBO

Game deck-building roguelike berbasis CLI yang menerapkan konsep OOP: enkapsulasi, inheritance, abstract base class, polimorfisme, operator overloading, dan relasi UML.

## Cara menjalankan

Gunakan Python 3.10 atau lebih baru. Tidak ada dependency eksternal.

```bash
python game.py
```

Pilih menu **3 — Demonstrasi OOP** untuk menampilkan bukti abstraksi, validasi setter, class/static method, operator overloading, dan duck typing. Smoke test otomatis dapat dijalankan dengan `python -m unittest test_oop.py`.

## GDD yang diterapkan

- Pertarungan turn-based melawan 1–3 musuh yang dipilih acak; statistik dan reward musuh meningkat setiap ronde.
- Statistik karakter: HP, MP, Strength, Intelligence, dan Speed.
- Basic Attack, Play Card, Draw Card, Discard Card, Block, Scan Enemy, dan Run.
- Kartu physical membayar cost menggunakan HP; kartu elemental/support membayar cost menggunakan MP.
- Affinity `WEAKNESS` menggandakan damage dan memberi Extra Turn; `STRENGTH` meniadakan damage; `NEUTRAL` memberi damage normal.
- Total card-score deck dibatasi 10 dan hand default maksimal 3 kartu. Next Card Preview menampilkan kartu berikutnya yang akan ditarik.
- Kartu yang dipakai/dibuang masuk discard pile. Membuang kartu berbiaya MP mengembalikan 15% cost MP (dibulatkan ke bawah).
- Setelah menang, pemain mendapat gold dan dapat meng-upgrade kartu yang dimiliki, membeli kartu baru, meningkatkan statistik, atau memulihkan HP/MP di shop.

## Struktur file

```text
.
├── main.py             # Model, kartu, deck, karakter, battle, shop
├── game.py             # Menu utama dan core game loop
├── test_oop.py         # Smoke tests untuk ketentuan OOP utama
├── class_diagram.png   # Diagram kelas untuk laporan
└── README.md
```

## Class diagram

![Class diagram Echoes of the Deck](class_diagram.png)

### Relasi UML yang benar-benar digunakan kode

- **Asosiasi — `Battle` dengan `Player` dan `Enemy`:** `Battle` menyimpan referensi ke pemain dan daftar musuh untuk satu encounter. Entitas tersebut dibuat di luar `Battle` dan tidak dibuat/dihancurkan oleh `Battle`.
- **Agregasi — `Deck` dengan `Card`:** objek kartu dibuat di luar deck (misalnya oleh `Deck.starter_deck()` atau `Shop`) lalu disimpan dalam koleksi deck. Kartu dipindahkan di antara draw pile, hand, dan discard pile; kartu bukan bagian eksklusif dari siklus hidup objek `Deck`.
- **Komposisi — `Player` dengan `Deck`:** `Player.__init__()` membuat deck miliknya sendiri dan menyimpannya sebagai atribut `deck`. Deck ini menjadi bagian internal dari state pemain.

## Abstraksi dan inheritance

- **`Combatant`** adalah abstract base class turunan `ABC`. Abstract method-nya adalah `choose_action(battle)` dan `basic_attack_power()`. Method konkret yang digunakan bersama adalah `perform_basic_attack(target)`, selain method status dan pemulihan.
- **`Player`** dan **`Enemy`** mewarisi `Combatant`, memanggil `super().__init__(...)`, dan mengimplementasikan kedua abstract method. Implementasi `choose_action()` berbeda: pemain menerima pilihan aksi dari CLI, sedangkan musuh memilih aksi AI.
- **`Card`** juga merupakan abstract base class. Abstract method `play()`, `resource_name()`, dan property `card_type` diimplementasikan oleh kelas kartu konkret.
- Kelas kartu menggunakan inheritance bertingkat: `PhysicalCard` diturunkan menjadi `StrikeCard`, `SlashCard`, dan `PierceCard`; `ElementalCard` diturunkan menjadi `FireCard`, `WindCard`, `WaterCard`, dan `EarthCard`.

## Polimorfisme

1. **Via inheritance:** `Player.choose_action()` memanggil `Battle.player_turn()`, sedangkan `Enemy.choose_action()` menjalankan logika AI. Keduanya dipanggil melalui antarmuka `Combatant` dalam loop pertarungan.
2. **Duck typing:** `print_summary(item)` hanya membutuhkan objek yang menyediakan method `summary()`. Fungsi yang sama dipanggil untuk `Player` dan `Shop`, yang tidak berhubungan melalui inheritance.
3. **Operator overloading:** `Deck.__len__()` memungkinkan `len(deck)`, sementara `Deck.__eq__()` membandingkan total card-score dua deck dengan operator `==`.

## Enkapsulasi dan method

- `Combatant.hp` dan `Combatant.mp` menggunakan `@property` dan setter yang menolak nilai negatif/non-numerik; HP/MP dibatasi hingga nilai maksimum masing-masing.
- Data internal seperti `Combatant.__hp`, `Combatant.__mp`, `Combatant.__block`, `Card.__card_id`, dan koleksi internal `Deck` memakai atribut private.
- Atribut `_strength` dan `_intelligence` merupakan protected agar dapat diakses melalui kelas turunan.
- `Deck.starter_deck()` adalah `@classmethod`; `Deck.score_is_valid()` dan `Card.valid_cost()` adalah `@staticmethod`.

## Bukti abstraksi dan validasi

Jalankan `python game.py`, lalu pilih menu `3`. Program mencoba membuat objek `Combatant` secara langsung dan menangkap `TypeError`, membuktikan abstract class tidak bisa diinstansiasi. Demonstrasi juga menguji setter HP dengan nilai valid dan negatif, menampilkan hasil validasi card-score, operator overloading, serta duck typing.

Contoh bagian output:

```text
Abstract class tidak dapat diinstansiasi: Can't instantiate abstract class Combatant ...
HP valid diterima: 100
HP tidak valid ditolak: HP harus berupa angka non-negatif.
Card score valid (6/10): True
Jumlah kartu di deck Tester A: 5
Perbandingan deck (score): True
Player Tester A: HP 100/120, Gold 0
Shop ronde 1: 4 item tersedia
```

Untuk memenuhi bagian screenshot laporan, jalankan demonstrasi di terminal dan ambil screenshot output tersebut, lalu lampirkan pada laporan/posttest sesuai instruksi dosen.

## Catatan implementasi

- `Deck.total_score` menghitung seluruh kartu di draw pile, hand, dan discard pile agar pemindahan kartu tidak mengakali batas card-score.
- `Deck.hand` memberikan tuple agar daftar internal hand tidak dapat dimutasi langsung dari luar.
- Highscore saat ini dihitung selama satu sesi program, bukan disimpan permanen ke file.
