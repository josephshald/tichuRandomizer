import random
import xml.etree.ElementTree as ET
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


def save_to_xml(hands_list, filename='tichu_hands.xml'):
    root = ET.Element('TichuHands')

    for hands in hands_list:
        hands_elem = ET.SubElement(root, 'Hands')
        for player, cards in hands.items():
            player_elem = ET.SubElement(hands_elem, 'Player', name=player)
            for card in cards:
                card_elem = ET.SubElement(player_elem, 'Card')
                ET.SubElement(card_elem, 'Rank').text = card['rank']
                ET.SubElement(card_elem, 'Suit').text = card['suit']

    tree = ET.ElementTree(root)
    tree.write(filename)


def generate_pdf(hands, pdf_filename='tichu_hands.pdf'):
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    for player, cards in hands.items():
        c.drawString(20, 750, f"{player}'s hand:")
        image_offset = 20
        for i, card in enumerate(cards[:8]):
            rank = card["rank"]
            suit = card["suit"]
            image_path = f'path/to/images/{rank}_of_{suit.lower()}.png'  # Adjust the path based on your file structure
            c.drawInlineImage(image_path, 20 + i * 50, 720 - image_offset, width=40, height=60)
            image_offset += 70

        c.drawString(20, 650 - image_offset, f"Full hand for {player}:")
        for i, card in enumerate(cards):
            rank = card["rank"]
            suit = card["suit"]
            c.drawString(20, 630 - image_offset - i * 20, f"{rank} of {suit}")

        image_offset += len(cards) * 20 + 20  # Adjust the offset for the next player

    c.save()


if __name__ == "__main__":
    num_hands = 3  # Adjust as needed
    hands_list = []

    deck = create_tichu_deck()

    for _ in range(num_hands):
        hands = deal_cards(deck)
        deal_last_six_cards(deck, hands)
        sort_hands(hands)
        hands_list.append(hands)

    save_to_xml(hands_list)
    generate_pdf(hands_list[0])  # Generate PDF for the first set of hands as an example
