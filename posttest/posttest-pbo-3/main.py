from abc import ABC, abstractmethod
import random
import os

class Card(ABC):
    total_created = 0
    DEFAULT_MAX_CARD_SCORE = 10

    def __init__(self, name: str, description: str, card_score: int, cost: int = 0):
        if not name.strip():
            raise ValueError("Nama kartu tidak boleh kosong.")
        if card_score <= 0:
            raise ValueError("Card-score harus lebih besar dari 0.")
        if cost < 0:
            raise ValueError("Cost tidak boleh negatif.")
        self.name = name
        self.description = description
        self.card_score = card_score
        self.cost = cost
        self.__card_id = f"CARD-{Card.total_created + 1:03d}"
        Card.total_created += 1

    @property
    def card_id(self):
        return self.__card_id

    @abstractmethod
    def play(self, user: "Combatant", target: "Combatant") -> bool:
        pass

    @abstractmethod
    def resource_name(self) -> str:
        pass

    def describe(self) -> str:
        return f"{self.name} [{self.card_type}] | Skor {self.card_score} | Cost {self.cost} {self.resource_name()} — {self.description}"

    @property
    @abstractmethod
    def card_type(self) -> str:
        pass

    @staticmethod
    def valid_cost(cost: int) -> bool:
        return isinstance(cost, int) and cost >= 0


class PhysicalCard(Card):
    def __init__(self, name, description, card_score, cost, damage, physical_type="Strike"):
        super().__init__(name, description, card_score, cost)
        if damage < 0:
            raise ValueError("Damage tidak boleh negatif.")
        self.damage = damage
        self.physical_type = physical_type

    @property
    def card_type(self):
        return self.physical_type.upper()

    def resource_name(self):
        return "HP"

    def play(self, user, target):
        if user.hp <= self.cost:
            print("HP tidak cukup untuk menggunakan kartu ini (HP harus tersisa minimal 1).")
            return False
        user.hp -= self.cost
        dealt = target.receive_attack(self.damage + user.strength, self.card_type)
        print(f"{user.name} memainkan {self.name}: {dealt} damage.")
        return True


class StrikeCard(PhysicalCard):
    def __init__(self, name="Strike", description="Serangan fisik cepat", card_score=1, cost=5, damage=12):
        super().__init__(name, description, card_score, cost, damage, "STRIKE")


class SlashCard(PhysicalCard):
    def __init__(self, name="Slash", description="Tebasan kuat", card_score=2, cost=8, damage=20):
        super().__init__(name, description, card_score, cost, damage, "SLASH")


class PierceCard(PhysicalCard):
    def __init__(self, name="Pierce", description="Serangan menusuk", card_score=2, cost=7, damage=18):
        super().__init__(name, description, card_score, cost, damage, "PIERCE")


class ElementalCard(Card):
    def __init__(self, name, description, card_score, cost, damage, element):
        super().__init__(name, description, card_score, cost)
        if damage < 0:
            raise ValueError("Damage tidak boleh negatif.")
        self.damage = damage
        self.element = element.upper()

    @property
    def card_type(self):
        return self.element

    def resource_name(self):
        return "MP"

    def play(self, user, target):
        if user.mp < self.cost:
            print("MP tidak cukup.")
            return False
        user.mp -= self.cost
        dealt = target.receive_attack(self.damage + user.intelligence, self.element)
        print(f"{user.name} memainkan {self.name}: {dealt} damage.")
        return True


class FireCard(ElementalCard):
    def __init__(self, name="Fireball", description="Sihir api", card_score=2, cost=12, damage=22):
        super().__init__(name, description, card_score, cost, damage, "FIRE")


class WindCard(ElementalCard):
    def __init__(self, name="Gale", description="Hantaman angin", card_score=1, cost=8, damage=14):
        super().__init__(name, description, card_score, cost, damage, "WIND")


class WaterCard(ElementalCard):
    def __init__(self, name="Tidal Wave", description="Gelombang air", card_score=2, cost=10, damage=18):
        super().__init__(name, description, card_score, cost, damage, "WATER")


class EarthCard(ElementalCard):
    def __init__(self, name="Earth Spike", description="Paku tanah", card_score=2, cost=10, damage=19):
        super().__init__(name, description, card_score, cost, damage, "EARTH")


class HealCard(Card):
    def __init__(self, name="Mend", description="Memulihkan HP", card_score=2, cost=12, healing=25):
        super().__init__(name, description, card_score, cost)
        self.healing = healing

    @property
    def card_type(self):
        return "SUPPORT"

    def resource_name(self):
        return "MP"

    def play(self, user, target):
        if user.mp < self.cost:
            print("MP tidak cukup.")
            return False
        user.mp -= self.cost
        restored = user.restore_hp(self.healing)
        print(f"{user.name} memulihkan {restored} HP.")
        return True


class ScanCard(Card):
    def __init__(self, name="Scan", description="Melihat status musuh", card_score=1, cost=5):
        super().__init__(name, description, card_score, cost)

    @property
    def card_type(self):
        return "SUPPORT"

    def resource_name(self):
        return "MP"

    def play(self, user, target):
        if user.mp < self.cost:
            print("MP tidak cukup.")
            return False
        user.mp -= self.cost
        target.show_status()
        return True


class Deck:
    DEFAULT_MAX_CARD_SCORE = 10
    DEFAULT_MAX_HAND = 3

    def __init__(self, cards=None, max_card_score=None, max_hand=None):
        self.__cards = list(cards or [])
        self.max_card_score = (
            self.DEFAULT_MAX_CARD_SCORE if max_card_score is None else max_card_score
        )
        self.max_hand = self.DEFAULT_MAX_HAND if max_hand is None else max_hand
        if not isinstance(self.max_card_score, int) or self.max_card_score < 0:
            raise ValueError("Batas card-score harus berupa integer non-negatif.")
        if not isinstance(self.max_hand, int) or self.max_hand < 1:
            raise ValueError("Max hand harus berupa integer minimal 1.")
        self.__hand = []
        self.__discard_pile = []
        self.__next_card = None
        self._validate_score()

    @property
    def cards(self):
        return tuple(self.__cards)

    @property
    def hand(self):
        # Berikan salinan agar daftar internal hand tidak bisa diubah tanpa validasi.
        return tuple(self.__hand)

    @property
    def total_score(self):
        # Semua kartu tetap dihitung, baik berada di draw pile, hand, maupun discard pile.
        return sum(
            card.card_score
            for card in self.__cards + self.__hand + self.__discard_pile
        )

    @staticmethod
    def score_is_valid(score, limit=10):
        return (
            isinstance(score, int) and not isinstance(score, bool)
            and isinstance(limit, int) and not isinstance(limit, bool)
            and 0 <= score <= limit
        )

    @classmethod
    def starter_deck(cls):
        return cls([StrikeCard(), StrikeCard(), FireCard(), WindCard(), HealCard()])

    def _validate_score(self):
        if not self.score_is_valid(self.total_score, self.max_card_score):
            raise ValueError(f"Total card-score {self.total_score} melebihi batas {self.max_card_score}.")

    def add_card(self, card):
        if not isinstance(card, Card):
            raise TypeError("Deck hanya dapat menerima objek Card.")
        if self.total_score + card.card_score > self.max_card_score:
            return False
        self.__cards.append(card)
        return True

    def preview_next(self):
        if self.__next_card is None:
            candidates = self.__cards if self.__cards else self.__discard_pile
            self.__next_card = random.choice(candidates) if candidates else None
        return self.__next_card

    def draw(self):
        if len(self.__hand) >= self.max_hand:
            print("Hand penuh.")
            return None
        if not self.__cards:
            if not self.__discard_pile:
                print("Deck kosong.")
                return None
            self.__cards, self.__discard_pile = self.__discard_pile, []
            random.shuffle(self.__cards)
        card = self.preview_next()
        if card not in self.__cards:
            self.__cards, self.__discard_pile = self.__discard_pile, []
        self.__cards.remove(card)
        self.__next_card = None
        self.__hand.append(card)
        return card

    def discard(self, index):
        if not 0 <= index < len(self.__hand):
            return None
        card = self.__hand.pop(index)
        self.__discard_pile.append(card)
        return card

    def remove_from_hand(self, index):
        if not 0 <= index < len(self.__hand):
            return None
        card = self.__hand.pop(index)
        self.__discard_pile.append(card)
        return card

    def all_cards(self):
        return list(self.__cards) + list(self.__hand) + list(self.__discard_pile)

    def __len__(self):
        return len(self.__cards) + len(self.__hand) + len(self.__discard_pile)

    def __eq__(self, other):
        if not isinstance(other, Deck):
            return NotImplemented
        return self.total_score == other.total_score


class Combatant(ABC):
    def __init__(self, name, hp, mp, strength, intelligence, speed):
        self.name = name
        self.max_hp = hp
        self.max_mp = mp
        self._strength = strength
        self._intelligence = intelligence
        self.speed = speed
        self.__hp = hp
        self.__mp = mp
        self.__block = 0
        self.affinities = {}

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("HP harus berupa angka non-negatif.")
        self.__hp = min(value, self.max_hp)

    @property
    def mp(self):
        return self.__mp

    @mp.setter
    def mp(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("MP harus berupa angka non-negatif.")
        self.__mp = min(value, self.max_mp)

    @property
    def strength(self):
        return self._strength

    @strength.setter
    def strength(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Strength harus berupa integer non-negatif.")
        self._strength = value

    @property
    def intelligence(self):
        return self._intelligence

    @intelligence.setter
    def intelligence(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Intelligence harus berupa integer non-negatif.")
        self._intelligence = value

    @property
    def is_alive(self):
        return self.hp > 0

    def restore_hp(self, amount):
        before = self.hp
        self.hp = self.hp + max(0, amount)
        return self.hp - before

    def restore_mp(self, amount):
        before = self.mp
        self.mp = self.mp + max(0, amount)
        return self.mp - before

    def block(self, amount):
        self.__block = max(0, amount)
        print(f"{self.name} bersiap menahan {self.__block} damage.")

    def receive_attack(self, damage, attack_type):
        affinity = self.affinities.get(attack_type.upper(), "NEUTRAL")
        if affinity == "STRENGTH":
            print(f"{self.name} kuat terhadap {attack_type}; serangan tidak berefek!")
            return 0
        if affinity == "WEAKNESS":
            damage *= 2
            print(f"Kelemahan {self.name} terhadap {attack_type}! Damage menjadi dua kali lipat.")
        damage = max(0, int(damage))
        absorbed = min(self.__block, damage)
        self.__block -= absorbed
        actual = damage - absorbed
        self.hp = max(0, self.hp - actual)
        return actual

    def show_status(self):
        print(f"\n{self.name}: HP {self.hp}/{self.max_hp} | MP {self.mp}/{self.max_mp} | STR {self.strength} | INT {self.intelligence} | SPD {self.speed}")
        print("-" * 90)

    def show_weakness(self): 
        combatant_weakness = next((k for k, v in self.affinities.items() if v == "WEAKNESS"), None)
        print(f"{self.name} Lemah terhadap {combatant_weakness}")
        print("-" * 90)

    @abstractmethod
    def choose_action(self, battle: "Battle"):
        pass

    @abstractmethod
    def basic_attack_power(self):
        pass

    def perform_basic_attack(self, target):
        damage = target.receive_attack(self.basic_attack_power(), "STRIKE")
        print(f"{self.name} melakukan Basic Attack kepada {target.name} ({damage} damage)")
        return damage


class Player(Combatant):
    def __init__(self, name="Player"):
        super().__init__(name, hp=120, mp=60, strength=8, intelligence=7, speed=10)
        self.deck = Deck.starter_deck()
        self.gold = 0
        self.level = 1
        self.affinities = {"FIRE": "NEUTRAL", "WIND": "NEUTRAL", "WATER": "NEUTRAL", "EARTH": "NEUTRAL",
                           "STRIKE": "NEUTRAL", "SLASH": "NEUTRAL", "PIERCE": "NEUTRAL"}

    def choose_action(self, battle):
        return battle.player_turn(self)

    def basic_attack_power(self):
        return 8 + self.strength

    def summary(self):
        return f"Player {self.name}: HP {self.hp}/{self.max_hp}, Gold {self.gold}"


class Enemy(Combatant):
    def __init__(self, name, hp, mp, strength, intelligence, speed, gold_reward, affinities=None):
        super().__init__(name, hp, mp, strength, intelligence, speed)
        self.gold_reward = gold_reward
        self.affinities = affinities or {}

    def choose_action(self, battle):
        targets = [target for target in battle.party if target.is_alive]
        if not targets:
            return
        target = targets[0]
        if self.hp < self.max_hp * 0.3 and random.random() < 0.35:
            restored = self.restore_hp(10)
            print(f"{self.name} memulihkan {restored} HP.")
        elif random.random() < 0.25:
            self.block(10)
        else:
            self.perform_basic_attack(target)

    def basic_attack_power(self):
        return 5 + self.strength

    def summary(self):
        return f"Enemy {self.name}: HP {self.hp}/{self.max_hp}, reward {self.gold_reward} gold"


class Battle:
    def __init__(self, player, enemies, round_number=1):
        self.player = player
        self.enemies = list(enemies)
        self.party = [player]
        self.round_number = round_number
        self.escaped = False

    @property
    def is_over(self):
        return not self.player.is_alive or not any(enemy.is_alive for enemy in self.enemies) or self.escaped

    @property
    def victory(self):
        return self.player.is_alive and not any(enemy.is_alive for enemy in self.enemies) and not self.escaped

    def player_turn(self, player):
        player_menu = ["Basic Attack", "Play Card", "Draw Card", "Discard Card", "Block", "Scan Enemy", "Run"]
        
        while player.is_alive:
            # clear()
            for enemy in self.enemies:
                enemy.show_status()
            
            print(f"{player.name} | HP {player.hp}/{player.max_hp} | MP {player.mp}/{player.max_mp} | Gold {player.gold}")
            print("-" * 90)
            for index, menu in enumerate(player_menu): 
                print(f"[{index + 1}] {menu}")

            print("-" * 90)
            choice = input("Aksi: ").strip()
            target = next((enemy for enemy in self.enemies if enemy.is_alive), None)
            print("-" * 90)
            
            if choice == "1":
                player.perform_basic_attack(target)
                return
            
            if choice == "2":
                if not player.deck.hand:
                    print("Hand kosong. Draw kartu terlebih dahulu.")
                    continue
                for i, card in enumerate(player.deck.hand, 1):
                    print(f"[{i}] {card.describe()}")
                try:
                    index = int(input("Nomor kartu (0 batal): "))
                except ValueError:
                    print("Masukkan angka.")
                    continue
                if index == 0:
                    continue
                card = player.deck.hand[index - 1] if 1 <= index <= len(player.deck.hand) else None
                if card is None:
                    print("Nomor kartu tidak valid.")
                    continue
                if card.play(player, target or player):
                    if target and target.affinities.get(card.card_type, "NEUTRAL") == "WEAKNESS":
                        player.extra_turn = True
                    player.deck.remove_from_hand(index - 1)
                    return
                continue
            
            if choice == "3":
                card = player.deck.draw()
                if card:
                    print(f"Kartu ditarik: {card.name}")
                    preview = player.deck.preview_next()
                    print(f"Next Preview Kartu Selanjutnya: {preview.name if preview else '(Deck kosong)'}")
                    print("-" * 90)
                return
            
            if choice == "4":
                if not player.deck.hand:
                    print("Hand kosong.")
                    continue
                for i, card in enumerate(player.deck.hand, 1):
                    print(f"[{i}] {card.name} (cost MP {card.cost})")
                try:
                    index = int(input("Nomor kartu yang dibuang: "))
                except ValueError:
                    print("Masukkan angka.")
                    continue
                card = player.deck.discard(index - 1)
                
                if card:
                    refund = int(card.cost * 0.15) if card.resource_name() == "MP" else 0
                    player.restore_mp(refund)
                    print(f"{card.name} dibuang. MP dipulihkan: {refund}.")
                    return
                
                print("Nomor kartu tidak valid.")
                continue
            
            if choice == "5":
                player.block(15)
                return
            
            if choice == "6":
                if target:
                    target.show_status()
                    target.show_weakness()
                return
            
            if choice == "7":
                if random.random() < 0.9:
                    print("Berhasil melarikan diri.")
                    self.escaped = True
                else:
                    print("Gagal melarikan diri!")
                return
            print("Pilihan tidak valid.")

    def run(self):
        clear()
        print(f"===> COMBAT ROUND {self.round_number}")
        
        # Speed menentukan urutan. saat seri, pemain mendapat prioritas.
        turn_order = sorted([self.player] + self.enemies, key=lambda entity: (entity.speed, entity is self.player), reverse=True)
        while not self.is_over:
            for entity in turn_order:
                if self.is_over:
                    break
                if not entity.is_alive:
                    continue
                entity.choose_action(self)
                if not self.is_over and entity is self.player:
                    # Kelemahan target memberi satu aksi ekstra.
                    if getattr(self, "extra_turn", False):
                        self.extra_turn = False
                        print("Weakness! Pemain memperoleh Extra Turn.")
                        entity.choose_action(self)
                        self.extra_turn = False
        
        if self.escaped:
            print("Pertarungan diakhiri dengan kabur.")
            print("-" * 90)
        elif self.victory:
            print("Semua musuh dikalahkan!")
            print("-" * 90)
        else:
            print("Pemain kalah.")
            print("-" * 90)
        return self.victory


class Shop:
    def __init__(self, player, round_number):
        self.player = player
        self.round_number = round_number
        self.stock = [
            (StrikeCard("Heavy Strike", "Serangan fisik lebih kuat", 2, 8, 24), 20),
            (FireCard("Inferno", "Sihir api kuat", 2, 15, 30), 25),
            (HealCard("Greater Mend", "Pemulihan lebih besar", 2, 15, 40), 22),
            (WindCard("Cyclone", "Serangan angin", 1, 10, 20), 18),
        ]

    def summary(self):
        return f"Shop ronde {self.round_number}: {len(self.stock)} item tersedia"

    def visit(self):
        shop_menu = [
            "Beli Kartu", 
            "Upgrade Kartu (+5 Power, 12 Gold)", 
            "Upgrade Strength (+2, 20 Gold)", 
            "Upgrade Max HP (+15, 20 Gold)", 
            "Pulihkan HP/MP (10 Gold)", 
            "Keluar Shop (Lanjut ke Ronde Selanjutnya)"
        ]
        
        while True:
            print(f"===> SHOP | Gold: {self.player.gold} | Card-score: {self.player.deck.total_score}/{self.player.deck.max_card_score}")

            for index, menu in enumerate(shop_menu): 
                print(f"[{index + 1}] {menu}")

            print("-" * 90)
            choice = input("Pilihan: ").strip()
            print("-" * 90)
            
            if choice == "6":
                return
            if choice == "1":
                for i, (card, price) in enumerate(self.stock, 1):
                    print(f"[{i}] {card.describe()} | Harga {price} gold")
                try:
                    print("-" * 90)
                    index = int(input("Pilih kartu (0 batal): "))
                except ValueError:
                    print("-" * 90)
                    print("Masukkan angka.")
                    print("-" * 90)
                    continue
                if index == 0:
                    continue
                if not 1 <= index <= len(self.stock):
                    print("-" * 90)
                    print("Pilihan tidak valid.")
                    print("-" * 90)
                    continue
                card, price = self.stock[index - 1]
                if self.player.gold < price:
                    print("-" * 90)
                    print("Gold tidak cukup.")
                    print("-" * 90)
                elif not self.player.deck.add_card(card):
                    print("Card-score deck akan melewati batas 10.")
                else:
                    self.player.gold -= price
                    self.stock.pop(index - 1)
                    print(f"{card.name} ditambahkan ke deck.")
            
            elif choice == "2":
                owned_cards = self.player.deck.all_cards()
                upgradeable = [
                    card for card in owned_cards
                    if hasattr(card, "damage") or hasattr(card, "healing")
                ]
                if not upgradeable:
                    print("Tidak ada kartu yang dapat di-upgrade.")
                    continue
                for i, card in enumerate(upgradeable, 1):
                    power = card.damage if hasattr(card, "damage") else card.healing
                    print(f"[{i}] {card.name} | Power saat ini: {power}")
                try:
                    print("-" * 90)
                    index = int(input("Pilih kartu (0 batal): "))
                    print("-" * 90)
                except ValueError:
                    print("Masukkan angka.")
                    print("-" * 90)
                    continue
                if index == 0:
                    continue
                if not 1 <= index <= len(upgradeable):
                    print("Pilihan tidak valid.")
                    continue
                if self.player.gold < 12:
                    print("Gold tidak cukup (butuh 12 gold).")
                    print("-" * 90)
                    continue
                card = upgradeable[index - 1]
                
                if hasattr(card, "damage"):
                    card.damage += 5
                    new_power = card.damage
                else:
                    card.healing += 5
                    new_power = card.healing
                self.player.gold -= 12
                print(f"{card.name} berhasil di-upgrade. Power sekarang: {new_power}.")
                print("-" * 90)
            
            elif choice == "3":
                if self.player.gold >= 20:
                    self.player.gold -= 20
                    self.player.strength += 2
                    print("Strength meningkat.")
                    print("-" * 90)
                else:
                    print("Gold tidak cukup.")
                    print("-" * 90)
            
            elif choice == "4":
                if self.player.gold >= 20:
                    self.player.gold -= 20
                    self.player.max_hp += 15
                    self.player.hp = self.player.hp + 15
                    print("Max HP meningkat.")
                    print("-" * 90)
                else:
                    print("Gold tidak cukup.")
                    print("-" * 90)
            
            elif choice == "5":
                if self.player.gold >= 10:
                    self.player.gold -= 10
                    self.player.restore_hp(30)
                    self.player.restore_mp(20)
                    print("HP dan MP dipulihkan.")
                    print("-" * 90)
                else:
                    print("Gold tidak cukup.")
                    print("-" * 90)
            else:
                print("Pilihan tidak valid.")
                print("-" * 90)


def create_enemy(round_number, index):
    templates = [
        ("Ash Slime", 35, 8, 4, 3, 5, {"FIRE": "STRENGTH", "WATER": "WEAKNESS"}),
        ("Gale Crow", 42, 12, 5, 5, 13, {"WIND": "STRENGTH", "EARTH": "WEAKNESS"}),
        ("Stone Guard", 55, 5, 7, 2, 4, {"EARTH": "STRENGTH", "PIERCE": "WEAKNESS"}),
        ("Tide Wisp", 38, 18, 3, 7, 9, {"WATER": "STRENGTH", "FIRE": "WEAKNESS"}),
    ]
    name, hp, mp, strength, intelligence, speed, affinities = random.choice(templates)
    scale = round_number - 1
    return Enemy(f"{name} #{index}", hp + scale * 8, mp + scale * 2, strength + scale, intelligence + scale, speed, 8 + scale * 3, affinities)


def print_summary(item):
    # Duck typing: menerima objek apa pun yang menyediakan summary().
    print(item.summary())


def demonstrate_oop():
    clear()
    print("=== DEMONSTRASI OOP ===")
    try:
        Combatant("Abstrak", 10, 10, 1, 1, 1)
    except TypeError as error:
        print(f"Abstract class tidak dapat diinstansiasi: {error}")
    p1, p2 = Player("Tester A"), Player("Tester B")
    print("Validasi setter HP:")
    p1.hp = 100
    print(f"HP valid diterima: {p1.hp}")
    try:
        p1.hp = -5
    except ValueError as error:
        print(f"HP tidak valid ditolak: {error}")
    print(f"Card score valid (6/10): {Deck.score_is_valid(6)}")
    print(f"Total kartu yang dibuat: {Card.total_created}")
    # Operator overloading: Deck mendukung len() dan penjumlahan score.
    print(f"Jumlah kartu di deck Tester A: {len(p1.deck)}")
    print(f"Perbandingan deck (score): {p1.deck == p2.deck}")
    print("Duck typing:")
    print_summary(p1)
    print_summary(Shop(p2, 1))
    input("Tekan Enter untuk melanjutkan...")

def clear(): 
    os.system('clear')
    os.system('cls')