import random
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_tichu_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['Jade', 'Pagoda', 'Star', 'Sword']
    special_cards = ['Mahjong', 'Dog', 'Phoenix', 'Dragon']
    deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits] + [{'rank': card, 'suit': 'Special'} for
                                                                                 card in special_cards]
    random.shuffle(deck)
    return deck


def deal_cards(deck, players=["North", "South", "East", "West"], cards_per_hand=8):
    hands = {player: [] for player in players}

    for _ in range(cards_per_hand):
        for player in hands:
            card = deck.pop()
            hands[player].append(card)

    return hands


def deal_last_six_cards(deck, hands):
    for _ in range(6):
        for player in hands:
            card = deck.pop()
            hands[player].append(card)


def sort_hands(hands):
    rank_order = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11,
                  'A': 12, 'Mahjong': 13, 'Dog': 14, 'Phoenix': 15, 'Dragon': 16}
    suit_order = {'Jade': 0, 'Pagoda': 1, 'Star': 2, 'Sword': 3, 'Special': 4}

    for player in hands:
        hands[player] = sorted(hands[player], key=lambda x: (suit_order[x['suit']], rank_order[x['rank']]))


def save_to_json(hands_list, filename='tichu_hands.json'):
    with open(filename, 'w') as json_file:
        json.dump(hands_list, json_file, indent=4)


def generate_pdf(hands, pdf_filename='tichu_hands.pdf'):
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    for player, cards in hands.items():
        c.drawString(20, 750, f"{player}'s hand:")

        image_offset_x = 20
        image_offset_y = 700
        card_width = 40
        card_height = 60

        for i, card in enumerate(cards[:8]):
            rank = card["rank"]
            suit = card["suit"]
            image_path = f'images/{rank}_of_{suit.lower()}.JPG'  # Adjust the path based on your file structure
            c.drawInlineImage(image_path, image_offset_x, image_offset_y, width=card_width, height=card_height)

            if i % 4 == 3:
                image_offset_y -= card_height
                image_offset_x = 20
            else:
                image_offset_x += card_width + 10

        image_offset_y -= card_height + 20  # Adjust the offset for the next player

    c.save()


if __name__ == "__main__":
    num_hands = 1  # Adjust as needed
    hands_list = []

    deck = create_tichu_deck()

    for _ in range(num_hands):
        hands = deal_cards(deck)
        deal_last_six_cards(deck, hands)
        sort_hands(hands)
        hands_list.append(hands)

    save_to_json(hands_list)
    generate_pdf(hands_list[0])  # Generate PDF for the first set of hands as an example
