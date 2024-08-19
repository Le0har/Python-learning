import random

# Начнем с создания карты
# ♥ ♦ ♣ ♠
VALUES = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
SUITS = ('Spades', 'Clubs', 'Diamonds', 'Hearts')
SUITS_UNI = {
        'Spades': '♠',
        'Clubs': '♣',
        'Diamonds': '♦',
        'Hearts': '♥'
}


class Card:
    def __init__(self, value, suit):
        self.value = value  # Значение карты(2, 3... 10, J, Q, K, A)
        self.suit = suit    # Масть карты

    def to_str(self):
        return f'{self.value}{SUITS_UNI[self.suit]}'

    def equal_suit(self, other_card):
        return self.suit == other_card.suit
    
    def __gt__(self, other_card):
        if SUITS.index(self.suit) == SUITS.index(other_card.suit):
            if VALUES.index(self.value) > VALUES.index(other_card.value):
                return True
        return False

    def __eq__(self, other_card):
        return VALUES.index(self.value) == VALUES.index(other_card.value)

    def __repr__(self):
        return f'{self.value}{SUITS_UNI[self.suit]}'

    def __str__(self):
        return f'{self.value}{SUITS_UNI[self.suit]}'
    

# Теперь создадим колоду из 52-ух карт и реализуем все методы
class Deck:
    def __init__(self):
        self.cards = []
        for suit in SUITS:
            for value in VALUES:
                card = Card(value, suit)
                self.cards.append(card)

    def __str__(self):
        new_str = f'deck[{len(self.cards)}]: '
        for card in self.cards:
            new_str += f'{card.value}{SUITS_UNI[card.suit]}, '
        return new_str

    def show(self):         # показать колоду карт
        print(str(self))

    def draw(self, x):      # Возьмем x карт "в руку"
        deleted_cards = []
        for i in range(x):
            deleted_cards.append(self.cards[0])
            del self.cards[0]
        return deleted_cards

    def shuffle(self):      # Тасуем колоду
        random.shuffle(self.cards)


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def take_in_hand(self, koloda, x):      # взять карты из колоды
        self.hand = Deck.draw(koloda, x)

    def show_hand(self):        # показать карты в руке
        print(f'В руке игрока {self.name} карт({len(self.hand)}): {self.hand}')

    def move(self, field):     # ходить самой мальнькой картой
        if len(self.hand) != 0:
            min_card = self.hand[0]
            for card in self.hand:
                if VALUES.index(card.value) < VALUES.index(min_card.value):
                    min_card = card
            Field.append_card(field, min_card)
            self.hand.remove(min_card)
            print(f'Ход игрока {self.name}: {min_card}')
        else:           # если карт в руке больше нет
            print(f'Карты в руке игрока {self.name} закончились!')
    
    def defend(self, current_card):     # пытается отбить карту
        for card in self.hand:
            if card > current_card:
                defend_card = card
                Field.append_card(field, defend_card)
                self.hand.remove(card)
                return True
        else:
            return False
            
    def move_extra(self, field):
        all_card_on_field = Field.get_all_card(field)
        for card_field in all_card_on_field:
            for card_hand in self.hand:
                if card_field == card_hand:
                    print(f'Игрок {self.name} подкидывает карту: {card_hand}')
                    Field.append_card(field, card_hand)
                    self.hand.remove(card_hand)
                    return True
        else:
            print(f'Игроку {self.name} нечего подкинуть! Переход хода!')
            return False


class Field:
    def __init__(self):
        self.cards_on_field = []

    def append_card(self, card):    # добавить карту на поле
        self.cards_on_field.append(card)

    def show(self):                 # показать какие карты на поле 
        print(f'На поле сейчас карты: {self.cards_on_field}')

    def get_last_card(self):        # узнать последнюю карту на поле
        if len(self.cards_on_field) != 0:
            return self.cards_on_field[-1]
        
    def get_all_card(self):         # узнать все карты на поле
        return self.cards_on_field


# 1. Создайте колоду из 52 карт. Перемешайте ее.
deck = Deck()
deck.shuffle()
print(deck)

# 2. Первый игрок берет сверху 10 карт.
player_1 = Player('Иван')
player_1.take_in_hand(deck, 10)
player_1.show_hand()

# 3. Второй игрок берет сверху 10 карт.
player_2 = Player('Маша')
player_2.take_in_hand(deck, 10)
player_2.show_hand()

# 4. Игрок-1 ходит:
# 4.1. игрок-1 выкладывает самую маленькую карту по "старшенству".
field = Field()     #создаем поле
player_1.move(field)
field.show()

# 4.2. игрок-2 пытается бить карту, если у него есть такая же масть, но значением больше.
trying_to_hit = player_2.defend(field.get_last_card())

# 4.3. Если игрок-2 не может побить карту, то он проигрывает/забирает себе(см. пункт 7).
if trying_to_hit == False:
    print(f'Нечем крыть! Игрок {player_2.name} проиграл!')

# 4.4. Если игрок-2 бьет карту, то игрок-1 может подкинуть карту любого значения, которое есть на столе.    
if trying_to_hit == True:
    print(f'Игрок {player_2.name} отбивается картой: {field.get_last_card()}')
    field.show()
    if player_1.move_extra(field) == True:      # если удалось подкинуть карту
        field.show()
        trying_to_hit = player_2.defend(field.get_last_card())      # пытается отбить подкинутую карты
        if trying_to_hit == False:
            print(f'Игрок {player_2.name} проиграл!')
        else:
            print(f'Игрок {player_2.name} отбивается картой: {field.get_last_card()}')
            field.show()
            print(f'Игрок {player_2.name} отбился! Переход хода!')

