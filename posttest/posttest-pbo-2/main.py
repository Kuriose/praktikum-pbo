import random

class Card:
    TIPE_KARTU = ["FIRE", "WATER", "PLANT"]
    __jumlah_kartu = 0

    def __init__(self, name, effect, damage, sp_cost, card_type):
        self.name = name
        self.effect = effect
        self._damage = damage
        self._sp_cost = sp_cost

        # Menentukan tipe Kartu
        if isinstance(card_type, int):
            self._card_type = Card.TIPE_KARTU[card_type - 1]
        else:
            self._card_type = str(card_type).upper()

        Card.__jumlah_kartu += 1
        self.__card_id = f"CARD-{Card.__jumlah_kartu:03d}"

    @property
    def damage(self):
        return self._damage

    @property
    def sp_cost(self):
        return self._sp_cost

    @property
    def card_type(self):
        return self._card_type

    @property
    def card_id(self):
        return self.__card_id

    def get_total_damage(self):
        return self._damage

    def describe(self):
        return f"{self.name} ({self._card_type}) - Damage: {self._damage}, SP: {self._sp_cost}"

    def activate(self, user, target):
        total = self.get_total_damage()
        print(f"{user.name} menggunakan {self.name} untuk memberikan {total} damage!")
        target.take_damage = total


class FireCard(Card):
    def __init__(self, name, effect, damage, sp_cost, burn_damage):
        super().__init__(name, effect, damage, sp_cost, card_type=1)
        self.burn_damage = burn_damage  # atribut unik FireCard

    def get_total_damage(self): 
        return super().get_total_damage() + self.burn_damage

    def describe(self):
        return super().describe() + f", Burn: +{self.burn_damage}"

    def activate(self, user, target):
        print(f"  ({self.effect}: tambahan {self.burn_damage} damage bakar!)")
        super().activate(user, target)


class WaterCard(Card):
    def __init__(self, name, effect, damage, sp_cost, mana_restore, hp_restore):
        super().__init__(name, effect, damage, sp_cost, card_type=2)
        self.mana_restore = mana_restore  # atribut unik WaterCard
        self.hp_restore = hp_restore

    def describe(self):
        return super().describe() + f", Pulihkan Mana: +{self.mana_restore}"

    def activate(self, user, target):
        super().activate(user, target)
        user.restore_mana(self.mana_restore)
        user.restore_health(self.hp_restore)
        print(f"  ({self.effect}) {user.name} memulihkan {self.mana_restore} mana!")
        print(f"  ({self.effect}) {user.name} memulihkan {self.hp_restore} health!")

class PlantCard(Card):
    def __init__(self, name, effect, damage, sp_cost, bind_turns):
        super().__init__(name, effect, damage, sp_cost, card_type=3)
        self.bind_turns = bind_turns  # atribut unik PlantCard

    def describe(self):
        return super().describe() + f", Ikat: {self.bind_turns} giliran"

    def activate(self, user, target):
        super().activate(user, target)
        target.apply_bind(self.bind_turns)
        print(f"  ({self.effect}) {target.name} terikat selama {self.bind_turns} giliran!")

class Deck:
    __discovered_card = []

    def __init__(self, list_card=None, base_hand=3, hand_multiplier=0):
        self.__list_card = list(list_card) if list_card else []
        self.__base_hand = base_hand
        self.__hand_multiplier = hand_multiplier

        for card in self.__list_card:
            Deck.__discovered_card.append(card)

    @property
    def list_card(self):
        return list(self.__list_card)

    @property
    def max_hand(self):
        return self.__base_hand + (2 * self.__hand_multiplier)

    @property
    def is_full(self):
        return len(self.__list_card) >= self.max_hand

    @classmethod
    def get_discovered_card(cls):
        return list(cls.__discovered_card)

    def draw_card(self):
        if self.is_full or not Deck.__discovered_card:
            return None

        random_card = random.choice(Deck.__discovered_card)
        self.__list_card.append(random_card)
        return random_card

    def use_card(self, card_number):
        if not 1 <= card_number <= len(self.__list_card):
            raise ValueError("Nomor Kartu tidak valid")

        return self.__list_card.pop(card_number - 1)

class Player:
    def __init__(self, name, health, mana, level=1, list_card=None):
        self.name = name
        self.__health = health
        self.__mana = mana
        self.level = level
        self.__isAlive = True
        self.__bound_turns = 0

        # Level 5 ke atas mendapat tambahan kapasitas hand
        hand_multiplier = 1 if self.level >= 5 else 0
        self.__deck = Deck(list_card, hand_multiplier=hand_multiplier)

    @property
    def list_card(self):
        return self.__deck.list_card

    def checkMaximumHand(self):
        return self.__deck.max_hand

    def use_card(self, card_number, target):
        if not isinstance(card_number, int):
            raise ValueError("Nomor Kartu yang dimasukkan harus angka")

        used_card = self.__deck.use_card(card_number)  # Kartu otomatis terhapus dari deck
        used_card.activate(self, target)

    def draw_card(self):
        if self.__deck.is_full:
            print(f"Hand {self.name} Penuh! Tidak bisa menarik Kartu!")
            return

        random_card = self.__deck.draw_card()
        if random_card is None:
            print("Tidak ada kartu yang bisa ditarik!")
            return

        print(f"{self.name} Mengambil Kartu {random_card.name} dari Deck")

    @staticmethod
    def calculateExpGain(value):
        expGained = 1 + (value * 0.1)
        return expGained

    @property
    def health(self):
        return self.__health

    @health.setter
    def take_damage(self, damage_taken):
        if not isinstance(damage_taken, int):
            raise ValueError("Damage yang dimasukkan harus berupa Integer")

        print(f"{self.name} Menerima damage sebesar {damage_taken}")
        self.__health -= damage_taken

        if self.__health <= 0:
            self.__health = 0
            self.__isAlive = False

    def restore_health(self, amount): 
        self.__health += amount

    @property
    def mana(self):
        return self.__mana

    @mana.setter
    def reduce_mana(self, amount):
        self.__mana -= amount

    def restore_mana(self, amount):
        self.__mana += amount

    # Status terikat (dipakai PlantCard)
    def apply_bind(self, turns):
        self.__bound_turns += turns

    def consume_bind(self):
        if self.__bound_turns > 0:
            self.__bound_turns -= 1
            return True
        return False

    @property
    def is_alive(self):
        return self.__isAlive
