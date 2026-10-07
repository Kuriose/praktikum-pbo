# Card Game Sederhana (Posttest 2)

Card Game / Deck Building berbasis terminal. Versi ini merupakan pembaruan dari Posttest sebelumnya dengan penambahan **Relasi UML** (asosiasi, agregasi, komposisi) dan **Inheritance** (pewarisan).

---

## Daftar Isi

1. [Penjelasan Program](#1-penjelasan-program)
2. [Cara Menjalankan](#2-cara-menjalankan)
3. [Struktur File](#3-struktur-file)
4. [Ringkasan Perubahan dari Versi Sebelumnya](#4-ringkasan-perubahan-dari-versi-sebelumnya)
5. [Struktur Class](#5-struktur-class)
6. [Relasi UML](#6-relasi-uml)
7. [Inheritance](#7-inheritance)
8. [Alur Kerja Program](#8-alur-kerja-program)
9. [Penerapan Enkapsulasi](#9-penerapan-enkapsulasi)
10. [Game Loop (`game.py`)](#10-game-loop-gamepy)

---

## 1. Penjelasan Program

Program ini memodelkan mekanisme dasar card game:

- **Kartu (`Card`)** adalah *superclass* yang memiliki nama, efek, damage, biaya SP, dan tipe elemen. Dari `Card` diturunkan tiga jenis kartu: **`FireCard`**, **`WaterCard`**, dan **`PlantCard`**, yang masing-masing punya atribut dan perilaku khusus.
- **Deck (`Deck`)** mengelola kartu di tangan pemain: menarik kartu acak, memakai kartu, dan membatasi jumlah kartu (max hand).
- **Pemain (`Player`)** memiliki health, mana, level, serta sebuah `Deck`. Pemain dapat memakai kartu untuk menyerang pemain lain, menarik kartu, dan menerima damage.

### Data awal (contoh di `game.py`)

| Kartu | Kelas | Efek | Damage | SP Cost | Atribut Unik |
|---|---|---|---|---|---|
| Fire Breath | `FireCard` | Membakar Musuh | 100 | 10 | `burn_damage = 20` |
| Water Blessing | `WaterCard` | Menenggelamkan Musuh | 90 | 0 | `mana_restore = 10` |
| Plant Sprout | `PlantCard` | Mengikat Musuh | 50 | 15 | `bind_turns = 1` |

| Pemain | Health | Mana | Level | Kartu Awal | Max Hand |
|---|---|---|---|---|---|
| Warrior | 100 | 90 | 5 | Fire Breath, Water Blessing | 5 |
| Novice | 250 | 80 | 2 | Water Blessing, Plant Sprout, Fire Breath | 3 |

Data awal ini belum bersifat final, sehingga nilai kartu maupun pemain masih bisa berubah.

---

## 2. Cara Menjalankan

```bash
python game.py    # game interaktif 2 pemain (lihat bagian 10)
```

---

## 3. Struktur File

```
.
├── main.py        # Class Card (+ FireCard, WaterCard, PlantCard), Deck, Player
├── game.py        # Game loop interaktif untuk showcase method-method (lihat bagian 10)
└── README.md      # Dokumentasi ini
```

---

## 4. Ringkasan Perubahan dari Versi Sebelumnya

### 4.1 Perubahan di `main.py`

| No | Perubahan | Keterangan |
|---|---|---|
| 1 | `Card` dijadikan **superclass** | Atribut `_damage`, `_sp_cost`, `_card_type` kini *protected*; ditambah `__card_id` yang *private*. Akses dari luar lewat `@property`. |
| 2 | Tiga **subclass** baru | `FireCard`, `WaterCard`, `PlantCard`, masing-masing memanggil `super().__init__(...)`. |
| 3 | **Atribut unik** per subclass | `burn_damage`, `mana_restore`, `bind_turns`. |
| 4 | **Method overriding** | `get_total_damage()`, `describe()`, dan `activate()` didefinisikan ulang di subclass. |
| 5 | Method baru di `Card` | `get_total_damage()`, `describe()`, `activate(user, target)`. |
| 6 | `Player.use_card()` diubah | Tidak lagi langsung memberi damage, tetapi memanggil `used_card.activate(self, target)` sehingga efek kartu bergantung pada jenis kartunya (polymorphism). |
| 7 | Method baru di `Player` | `restore_mana()`, `apply_bind()`, `consume_bind()`, serta atribut private `__bound_turns`. |
| 8 | Komentar relasi UML | Penanda asosiasi, agregasi, dan komposisi pada `Deck` dan `Player`. |

### 4.2 Perubahan di `game.py`

| No | Perubahan | Keterangan |
|---|---|---|
| 1 | `import` | Dari `Card` menjadi `FireCard, WaterCard, PlantCard`. |
| 2 | `buat_pemain()` | Kartu dibuat dengan subclass masing-masing beserta atribut uniknya. |
| 3 | `tampilkan_kartu()` | Memakai `k.describe()` agar info khusus tiap kartu ikut tampil. |
| 4 | `game_loop()` | Di awal giliran dicek `aktif.consume_bind()`. Jika pemain sedang terikat (efek `PlantCard`), giliran dilewati. |

### 4.3 Yang tidak berubah

`Deck` (logika dan atribut private-nya), `Player.draw_card()`, `Player.calculateExpGain()`, setter `take_damage` dan `reduce_mana`, serta aturan main di `game.py` tetap sama seperti versi sebelumnya.

---

## 5. Struktur Class

### 5.1 Class `Card` (Superclass)

Atribut dan method yang dimiliki **semua** jenis kartu.

| Atribut | Akses | Tipe | Keterangan |
|---|---|---|---|
| `TIPE_KARTU` | public (konstanta class) | `list` | `["FIRE", "WATER", "PLANT"]` |
| `name` | public | `str` | Nama kartu |
| `effect` | public | `str` | Deskripsi efek |
| `_damage` | **protected** | `int` | Damage dasar. Dipakai langsung oleh subclass |
| `_sp_cost` | **protected** | `int` | Biaya SP |
| `_card_type` | **protected** | `str` | Diisi dari angka: `1` = FIRE, `2` = WATER, `3` = PLANT |
| `__card_id` | **private** | `str` | ID unik (`CARD-001`, `CARD-002`, ...). Hanya diatur oleh `Card` |
| `__jumlah_kartu` | **private** (class-level) | `int` | Penghitung untuk membuat `__card_id` |

| Member | Jenis | Keterangan |
|---|---|---|
| `damage`, `sp_cost`, `card_type`, `card_id` | property (read-only) | Akses baca ke atribut protected/private di atas |
| `get_total_damage()` | method | Mengembalikan damage yang akan diberikan (versi dasar: `_damage`) |
| `describe()` | method | Teks ringkas kartu untuk ditampilkan di game |
| `activate(user, target)` | method | Perilaku dasar kartu: memberi `get_total_damage()` ke `target` |

### 5.2 Subclass dari `Card`

| Subclass | Atribut Unik | `super().__init__` | Method yang di-override | Perilaku |
|---|---|---|---|---|
| `FireCard` | `burn_damage` | `card_type=1` | `get_total_damage()`, `describe()`, `activate()` | Total damage = `_damage + burn_damage`. Mencetak info damage bakar sebelum menyerang. |
| `WaterCard` | `mana_restore` | `card_type=2` | `describe()`, `activate()` | Menyerang seperti biasa, lalu memulihkan mana pemain yang memakai kartu. |
| `PlantCard` | `bind_turns` | `card_type=3` | `describe()`, `activate()` | Menyerang seperti biasa, lalu mengikat target sehingga melewati giliran sebanyak `bind_turns`. |

Setiap `activate()` di subclass memanggil `super().activate(user, target)` terlebih dahulu (atau setelahnya), lalu menambahkan logika khususnya.

### 5.3 Class `Deck`

Mengelola kartu di tangan pemain. Semua atributnya **private**.

| Atribut | Jenis | Keterangan |
|---|---|---|
| `__discovered_card` | class-level, private | Kumpulan semua kartu yang pernah dimasukkan ke deck mana pun. Dipakai bersama sebagai sumber kartu acak saat menarik kartu. |
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

### 5.4 Class `Player`

| Atribut | Jenis | Keterangan |
|---|---|---|
| `name` | public | Nama pemain |
| `level` | public | Level pemain. Level **≥ 5** memberi bonus kapasitas hand (`hand_multiplier = 1`, sehingga max hand menjadi 5) |
| `__health` | private | Nyawa pemain |
| `__mana` | private | Mana pemain |
| `__isAlive` | private | Status hidup/mati |
| `__bound_turns` | private | Sisa giliran yang harus dilewati karena terikat (efek `PlantCard`) |
| `__deck` | private | Objek `Deck` milik pemain |

| Member | Jenis | Keterangan |
|---|---|---|
| `list_card` | property | Daftar kartu di tangan (diteruskan dari `Deck`) |
| `health` | property | Membaca health |
| `take_damage` | setter | Mengurangi health, dipakai dengan `pemain.take_damage = 50`. Health tidak kurang dari 0 dan `is_alive` menjadi `False` jika health mencapai 0. Melempar `ValueError` jika bukan `int`. |
| `mana` | property | Membaca mana |
| `reduce_mana` | setter | Mengurangi mana, dipakai dengan `pemain.reduce_mana = 10` |
| `restore_mana(amount)` | method **(baru)** | Menambah mana. Dipanggil oleh `WaterCard.activate()` |
| `apply_bind(turns)` | method **(baru)** | Menambah jumlah giliran terikat. Dipanggil oleh `PlantCard.activate()` |
| `consume_bind()` | method **(baru)** | Mengurangi 1 giliran terikat. Mengembalikan `True` jika pemain harus melewati giliran |
| `is_alive` | property | Status hidup/mati |
| `use_card(card_number, target)` | method | Memakai kartu ke-`card_number` pada `target`. Kartu terhapus dari deck, lalu `kartu.activate(self, target)` dipanggil. |
| `draw_card()` | method | Menarik kartu acak. Mencetak pesan jika hand penuh. |
| `checkMaximumHand()` | method | Mengembalikan kapasitas maksimal hand |
| `calculateExpGain(value)` | staticmethod | Menghitung EXP: `1 + (value * 0.1)` |

---

## 6. Relasi UML
### 6.1 Penerapan tiap relasi

| Relasi | Hubungan | Notasi | Letak di kode | Alasan |
|---|---|---|---|---|
| **Asosiasi** | `Player` menggunakan `Player` lain | `..>` | `Player.use_card(card_number, target)` dan `Card.activate(user, target)` | Lawan (`target`) hanya diterima lewat parameter method dan tidak disimpan sebagai atribut. Kedua objek hidup mandiri. |
| **Agregasi** | `Deck` memiliki `Card` | `o--` | `Deck.__init__(list_card)`, kartu dibuat di `buat_pemain()` di `game.py` | `Card` dibuat **di luar** lalu dikirim lewat konstruktor. Deck hanya menampung referensi, jadi jika `Deck` dihapus, objek `Card` tetap ada. |
| **Komposisi** | `Player` terdiri dari `Deck` | `*--` | `self.__deck = Deck(...)` di `Player.__init__` | `Deck` dibuat **langsung di dalam** `Player`, bersifat private, dan hanya dimiliki satu pemain. Jika `Player` dihapus, `Deck`-nya ikut hilang. |

---

## 7. Inheritance

### 7.1 Pemenuhan ketentuan

| Ketentuan | Penerapan |
|---|---|
| Minimal 1 superclass dan 2 subclass | Superclass `Card`; subclass `FireCard`, `WaterCard`, `PlantCard` (3 subclass, *hierarchical inheritance*) |
| Memakai `super().__init__(...)` | Konstruktor ketiga subclass memanggil `super().__init__(name, effect, damage, sp_cost, card_type=...)` |
| Atribut unik per subclass | `FireCard.burn_damage`, `WaterCard.mana_restore`, `PlantCard.bind_turns` |
| Method overriding | `get_total_damage()` di `FireCard`; `describe()` dan `activate()` di ketiga subclass |
| Atribut *protected* | `_damage`, `_sp_cost`, `_card_type` di `Card`, dipakai langsung oleh subclass (mis. `FireCard` mengakses `_damage` lewat `super().get_total_damage()` dan `describe()`) |
| Atribut *private* | `__card_id` dan `__jumlah_kartu`: rahasia `Card`, tidak bisa diubah subclass |

### 7.2 Contoh method overriding

`get_total_damage()` pada `Card` hanya mengembalikan `_damage`. `FireCard` menimpanya dengan menambahkan damage bakar:

```python
class Card:
    def get_total_damage(self):
        return self._damage

class FireCard(Card):
    def get_total_damage(self):
        return super().get_total_damage() + self.burn_damage
```

Karena `Card.activate()` memakai `get_total_damage()`, kartu Fire Breath (damage 100, burn 20) memberikan **120 damage** tanpa `Card.activate()` perlu diubah.

---

## 8. Alur Kerja Program

### 8.1 Membuat pemain

```
Player(name, health, mana, level, list_card)
   ├─ simpan name, level, __health, __mana, __isAlive = True, __bound_turns = 0
   ├─ hand_multiplier = 1 jika level >= 5, selain itu 0
   └─ __deck = Deck(list_card, hand_multiplier)      <- KOMPOSISI
          └─ tiap kartu awal (dibuat di luar) dicatat   <- AGREGASI
             ke __discovered_card
```

### 8.2 Menarik kartu (`draw_card`)

```
Player.draw_card()
   ├─ Deck.is_full ?  ── ya ──> cetak "Hand ... Penuh!" lalu selesai
   └─ tidak
        └─ Deck.draw_card()
             ├─ pilih kartu acak dari __discovered_card
             ├─ tambahkan ke __list_card
             └─ kembalikan kartu ──> Player mencetak "... Mengambil Kartu ..."
```

### 8.3 Memakai kartu (`use_card`)

```
Player.use_card(nomor, target)                       <- ASOSIASI (target via parameter)
   ├─ nomor bukan int ? ──> ValueError
   ├─ Deck.use_card(nomor)   (nomor di luar 1..jumlah kartu ──> ValueError)
   │     └─ kartu dihapus dari hand dan dikembalikan
   └─ kartu.activate(self, target)                   <- versi subclass yang dijalankan
         ├─ FireCard : info burn -> super().activate() (damage = damage + burn)
         ├─ WaterCard: super().activate() -> user.restore_mana(mana_restore)
         └─ PlantCard: super().activate() -> target.apply_bind(bind_turns)
               └─ Card.activate(): cetak pesan, target.take_damage = total
                     └─ health target berkurang; jika <= 0 maka health = 0, is_alive = False
```

### 8.4 Efek ikat (`PlantCard`)

```
Awal giliran pemain (game_loop)
   └─ aktif.consume_bind()
        ├─ True  ──> cetak "terikat dan melewati giliran", giliran berpindah
        └─ False ──> giliran berjalan normal
```

---

## 9. Penerapan Enkapsulasi

| Tingkat akses | Penulisan | Dipakai pada | Alasan |
|---|---|---|---|
| **Public** | `name`, `effect`, `burn_damage`, ... | Data yang aman dibaca dan diubah dari luar | Tidak ada aturan khusus yang perlu dijaga |
| **Protected** | `_damage`, `_sp_cost`, `_card_type` | `Card`, dipakai oleh subclass | Subclass perlu mengakses atau memanipulasi langsung |
| **Private** | `__card_id`, `__jumlah_kartu` (di `Card`); semua atribut `Deck`; `__health`, `__mana`, `__isAlive`, `__bound_turns`, `__deck` (di `Player`) | Data rahasia milik class itu sendiri | Dilindungi dari perubahan langsung; akses lewat property atau method |

Catatan: atribut private mengalami *name mangling* (mis. `__card_id` menjadi `_Card__card_id`), sehingga subclass pun tidak bisa mengaksesnya langsung. Karena itu atribut yang perlu dipakai subclass dibuat protected, sedangkan sisanya tetap private.

---

## 10. Game Loop (`game.py`)

`game.py` adalah game loop sederhana berbasis giliran (*hot-seat*: dua pemain bergantian di terminal yang sama).

### 10.1 Aturan main

- Warrior dan Novice bergantian, dimulai dari Warrior.
- Pada setiap giliran, pemain memilih **satu aksi yang memakai giliran** (pakai kartu, tarik kartu, atau lewati). Melihat status tidak memakai giliran.
- Kartu hanya bisa dipakai jika mana cukup untuk membayar `sp_cost` kartu tersebut.
- Pemain yang terkena **Plant Sprout** melewati giliran berikutnya.
- Permainan berakhir saat health salah satu pemain mencapai 0. Pemenang mendapat EXP.

### 10.2 Menu aksi

| Pilihan | Aksi | Memakai giliran? |
|---|---|---|
| `1` | Pakai kartu (lalu pilih nomor kartu, `0` untuk batal) | Ya, jika berhasil |
| `2` | Tarik kartu | Ya, jika berhasil (hand belum penuh) |
| `3` | Lihat status | Tidak |
| `4` | Lewati giliran | Ya |
| `0` | Keluar dari game | - |

### 10.3 Method yang ditampilkan

| Bagian di game | Member yang dipakai |
|---|---|
| Membuat kartu | `FireCard`, `WaterCard`, `PlantCard` (agregasi ke `Deck` lewat `Player`) |
| Menampilkan kartu di tangan | `Player.list_card` (property) dan `Card.describe()` |
| Menampilkan health dan mana | `Player.health`, `Player.mana` (property) |
| Menampilkan kapasitas hand (mis. `2/5 kartu`) | `Player.checkMaximumHand()` |
| Memakai kartu | `Player.use_card()` → `Deck.use_card()` → `Card.activate()` (versi subclass) |
| Membayar biaya SP kartu | setter `Player.reduce_mana` |
| Menarik kartu | `Player.draw_card()` → `Deck.is_full` dan `Deck.draw_card()` |
| Melewati giliran karena terikat | `Player.consume_bind()` |
| Menentukan kapan game berakhir | `Player.is_alive` (property) |
| Memberi EXP kepada pemenang | `Player.calculateExpGain()` (staticmethod) |

Dua hal yang dijaga di level game loop, bukan di class:

- **Validasi input**: input non-angka dan nomor kartu di luar jangkauan ditolak dengan pesan, tanpa memakai giliran.
- **Pemotongan mana**: `Player.use_card()` belum mengurangi mana, jadi `game.py` yang memeriksa mana sebelum memakai kartu dan memanggil `reduce_mana` sesudahnya.

### 10.4 Contoh alur (dipersingkat)

```
Ronde 1 - Giliran Warrior
Health Warrior: 100 | Health Novice: 250
Pilih aksi: 1
  [1] Fire Breath (FIRE) - Damage: 100, SP: 10, Burn: +20
  [2] Water Blessing (WATER) - Damage: 90, SP: 0, Pulihkan Mana: +10
Pilih nomor kartu (0 = batal): 2
Warrior menggunakan Water Blessing untuk memberikan 90 damage!
Novice Menerima damage sebesar 90
  (Menenggelamkan Musuh) Warrior memulihkan 10 mana!
Sisa mana Warrior: 100
...
Novice MENANG!
Novice mendapatkan 1.2 EXP
```