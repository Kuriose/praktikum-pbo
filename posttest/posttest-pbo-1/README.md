# Card Game Sederhana

---

## Daftar Isi

1. [Penjelasan Program](#1-penjelasan-program)
2. [Cara Menjalankan](#2-cara-menjalankan)
3. [Struktur File](#3-struktur-file)
4. [Struktur Class](#4-struktur-class)
5. [Game Loop (`game.py`)](#6-game-loop-gamepy)

---

## 1. Penjelasan Program

Program ini memodelkan mekanisme dasar card game:

- **Kartu (`Card`)** memiliki nama, efek, damage, biaya SP, dan tipe elemen (FIRE, WATER, PLANT).
- **Deck (`Deck`)** mengelola kartu di tangan pemain: menarik kartu acak, memakai kartu, dan membatasi jumlah kartu (max hand).
- **Pemain (`Player`)** memiliki health, mana, level, serta sebuah `Deck`. Pemain dapat memakai kartu untuk menyerang pemain lain, menarik kartu, dan menerima damage.

### Data awal (contoh di `main.py`)

| Kartu | Efek | Damage | SP Cost | Tipe |
|---|---|---|---|---|
| Fire Breath | Membakar Musuh | 100 | 10 | FIRE |
| Water Blessing | Menenggelamkan Musuh | 90 | 0 | WATER |
| Plant Sprout | Mengikat Musuh | 50 | 15 | PLANT |

| Pemain | Health | Mana | Level | Kartu Awal | Max Hand |
|---|---|---|---|---|---|
| Warrior | 100 | 90 | 5 | Fire Breath, Water Blessing | 5 |
| Novice | 250 | 80 | 2 | Water Blessing, Plant Sprout, Fire Breath | 3 |

Data awal disini masih belum bersifat final, artinya perubahan bisa terjadi di kartu-kartu diatas. 

---

## 2. Cara Menjalankan

```bash
python game.py    # game interaktif 2 pemain (lihat bagian 8)
```

---

## 3. Struktur File

```
.
├── main.py        # Class Card, Deck, Player + contoh penggunaan 
├── game.py        # Game loop interaktif untuk showcase method-method (lihat bagian 8)
└── README.md      # Dokumentasi ini
```

---

## 4. Struktur Class

### 4.1 Class `Card`

Merepresentasikan satu kartu.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `TIPE_KARTU` | `list` (konstanta class) | `["FIRE", "WATER", "PLANT"]` |
| `name` | `str` | Nama kartu |
| `effect` | `str` | Deskripsi efek |
| `damage` | `int` | Damage yang diberikan ke target |
| `sp_cost` | `int` | Biaya SP (belum dipakai dalam perhitungan) |
| `card_type` | `str` | Diisi dari `card_type` berupa angka: `1` = FIRE, `2` = WATER, `3` = PLANT |

### 4.2 Class `Deck`

Mengelola kartu di tangan pemain. Semua atributnya **private**.

| Atribut | Jenis | Keterangan |
|---|---|---|
| `__discovered_card` | class-level, private | Kumpulan semua kartu yang pernah dimasukkan ke deck mana pun. Dipakai bersama oleh semua `Deck` sebagai sumber kartu acak saat menarik kartu. |
| `__list_card` | instance, private | Kartu yang sedang dipegang pemain |
| `__base_hand` | instance, private | Kapasitas dasar hand (default `3`) |
| `__hand_multiplier` | instance, private | Pengali bonus kapasitas hand (default `0`) |

| Member | Jenis | Keterangan |
|---|---|---|
| `list_card` | property (read-only) | Mengembalikan **salinan** daftar kartu di tangan |
| `max_hand` | property (read-only) | `__base_hand + (2 * __hand_multiplier)` |
| `is_full` | property (read-only) | `True` jika jumlah kartu sudah mencapai `max_hand` |
| `get_discovered_card()` | classmethod | Mengembalikan salinan daftar kartu yang pernah ditemukan |
| `draw_card()` | method | Mengambil satu kartu acak dari `__discovered_card` dan menambahkannya ke hand. Mengembalikan kartu tersebut, atau `None` jika hand penuh / belum ada kartu yang ditemukan. |
| `use_card(card_number)` | method | Mengambil dan **menghapus** kartu ke-`card_number` (mulai dari 1) dari hand. Melempar `ValueError` jika nomor di luar jangkauan. |

### 4.3 Class `Player`

Merepresentasikan pemain.

| Atribut | Jenis | Keterangan |
|---|---|---|
| `name` | public | Nama pemain |
| `level` | public | Level pemain. Level **≥ 5** memberi bonus kapasitas hand (`hand_multiplier = 1`, sehingga max hand menjadi 5) |
| `__health` | private | Nyawa pemain |
| `__mana` | private | Mana pemain |
| `__isAlive` | private | Status hidup/mati |
| `__deck` | private | Objek `Deck` milik pemain |

| Member | Jenis | Keterangan |
|---|---|---|
| `list_card` | property | Daftar kartu di tangan (diteruskan dari `Deck`) |
| `health` | property | Membaca health |
| `take_damage` | setter | Mengurangi health. Dipakai dengan sintaks `pemain.take_damage = 50`. Health tidak akan kurang dari 0 dan `is_alive` menjadi `False` jika health mencapai 0. Melempar `ValueError` jika bukan `int`. |
| `mana` | property | Membaca mana |
| `reduce_mana` | setter | Mengurangi mana, dipakai dengan `pemain.reduce_mana = 10` |
| `is_alive` | property | Status hidup/mati |
| `use_card(card_number, target)` | method | Memakai kartu ke-`card_number` untuk menyerang `target`. Kartu otomatis terhapus dari deck. |
| `draw_card()` | method | Menarik kartu acak. Mencetak pesan jika hand penuh. |
| `checkMaximumHand()` | method | Mengembalikan kapasitas maksimal hand |
| `calculateExpGain(value)` | staticmethod | Menghitung EXP: `1 + (value * 0.1)` |

---

## 5. Game Loop (`game.py`)

`game.py` adalah game loop sederhana berbasis giliran (*hot-seat*: dua pemain bergantian di terminal yang sama) untuk memperlihatkan method-method yang ada. Jalankan dengan:

```bash
python game.py
```

### 5.1 Aturan main

- Warrior dan Novice bergantian, dimulai dari Warrior.
- Pada setiap giliran, pemain memilih **satu aksi yang memakai giliran** (pakai kartu, tarik kartu, atau lewati). Melihat status tidak memakai giliran.
- Kartu hanya bisa dipakai jika mana cukup untuk membayar `sp_cost` kartu tersebut.
- Permainan berakhir saat health salah satu pemain mencapai 0. Pemenang mendapat EXP.

### 6.2 Menu aksi

| Pilihan | Aksi | Memakai giliran? |
|---|---|---|
| `1` | Pakai kartu (lalu pilih nomor kartu, `0` untuk batal) | Ya, jika berhasil |
| `2` | Tarik kartu | Ya, jika berhasil (hand belum penuh) |
| `3` | Lihat status | Tidak |
| `4` | Lewati giliran | Ya |
| `0` | Keluar dari game | - |

### 5.3 Method yang ditampilkan

| Bagian di game | Member yang dipakai |
|---|---|
| Menampilkan kartu di tangan | `Player.list_card` (property) |
| Menampilkan health dan mana | `Player.health`, `Player.mana` (property) |
| Menampilkan kapasitas hand (mis. `2/5 kartu`) | `Player.checkMaximumHand()` |
| Memakai kartu | `Player.use_card()` yang memanggil `Deck.use_card()` dan setter `take_damage` |
| Membayar biaya SP kartu | setter `Player.reduce_mana` |
| Menarik kartu | `Player.draw_card()` yang memanggil `Deck.is_full` dan `Deck.draw_card()` |
| Menentukan kapan game berakhir | `Player.is_alive` (property) |
| Memberi EXP kepada pemenang | `Player.calculateExpGain()` (staticmethod) |

### 5.4 Contoh alur (dipersingkat)

```
Ronde 1 - Giliran Warrior
Health Warrior: 100 | Health Novice: 250
Pilih aksi: 1
  [1] Fire Breath (FIRE) - Damage: 100, SP: 10
  [2] Water Blessing (WATER) - Damage: 90, SP: 0
Pilih nomor kartu (0 = batal): 1
Warrior menggunakan Fire Breath untuk memberikan 100 damage!
Novice Menerima damage sebesar 100
Sisa mana Warrior: 80
...
Novice MENANG!
Novice mendapatkan 1.2 EXP
```

---
