import random

class Card: 
    TIPE_KARTU = ["FIRE", "WATER", "PLANT"] 

    def __init__(self, name, effect, damage, sp_cost, card_type):
        self.name = name
        self.effect = effect
        self.sp_cost = sp_cost
        self.damage = damage

        #  Menentukan tipe Kartu
        if isinstance(card_type, int):
            self.card_type = Card.TIPE_KARTU[card_type - 1]    


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
        print(f"{self.name} menggunakan {used_card.name} untuk memberikan {used_card.damage} damage!")
        target.take_damage = used_card.damage

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

    @property        
    def mana(self): 
        return self.__mana

    @mana.setter
    def reduce_mana(self, amount):
        self.__mana -= amount

    @property
    def is_alive(self): 
        return self.__isAlive 