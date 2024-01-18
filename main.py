import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph


def create_tichu_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['Jade', 'Pagoda', 'Star', 'Sword']
    special_cards = ['Mahjong', 'Dog', 'Phoenix', 'Dragon']
    deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits] + [{'rank': card, 'suit': 'Special'} for
                                                                                 card in special_cards]
    random.shuffle(deck)
    return deck


def deal_cards(deck, players=["North", "South", "East", "West"], cards_per_hand=8):
    hands = {player: {'all_cards': [], 'first_8_cards': []} for player in players}

    for _ in range(cards_per_hand):
        for player in hands:
            card = deck.pop()
            hands[player]['all_cards'].append(card)
            if len(hands[player]['first_8_cards']) < 8:
                hands[player]['first_8_cards'].append(card)

    return hands


def deal_last_six_cards(deck, hands):
    for _ in range(6):
        for player in hands:
            card = deck.pop()
            hands[player]['all_cards'].append(card)


def sort_hands(hands):
    rank_order = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11,
                  'A': 12, 'Mahjong': 13, 'Dog': 14, 'Phoenix': 15, 'Dragon': 16}
    suit_order = {'Jade': 0, 'Pagoda': 1, 'Star': 2, 'Sword': 3, 'Special': 4}

    for player, cards_info in hands.items():
        hands[player]['all_cards'] = sorted(cards_info['all_cards'],
                                            key=lambda x: (suit_order[x['suit']], rank_order[x['rank']]))
        hands[player]['first_8_cards'] = sorted(cards_info['first_8_cards'],
                                                key=lambda x: (suit_order[x['suit']], rank_order[x['rank']]))


def generate_pdf(hands, pdf_filename='tichu_hands.pdf'):
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    player_positions = {
        'North': (20, 750),
        'South': (300, 750),
        'East': (20, 400),
        'West': (300, 400)
    }

    card_width = 40
    card_height = 60
    grid_spacing = 10

    for hand_num, (player, cards_info) in enumerate(hands.items(), start=1):
        hand_label = f"Hand {hand_num} - {player}'s hand:"

        # Create a custom style for bold text
        bold_style = ParagraphStyle(
            'BoldText',
            parent=getSampleStyleSheet()['BodyText'],
            fontName='Helvetica-Bold'
        )

        # Use Paragraph to draw text with custom style
        p = Paragraph(hand_label, style=bold_style)
        p.wrapOn(c, 400, 20)
        p.drawOn(c, player_positions[player][0], player_positions[player][1] + 50)

        image_offset_x = player_positions[player][0]
        image_offset_y = player_positions[player][1] - 20
        row_count = 0

        for i, card in enumerate(cards_info['first_8_cards']):
            rank = card["rank"]
            suit = card["suit"]
            image_path = f'images/{rank}_of_{suit.lower()}.JPG'  # Adjust the path based on your file structure
            c.drawInlineImage(image_path, image_offset_x, image_offset_y, width=card_width, height=card_height)

            row_count += 1
            if row_count == 4:
                image_offset_y -= card_height + grid_spacing
                image_offset_x = player_positions[player][0]
                row_count = 0
            else:
                image_offset_x += card_width + grid_spacing

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

    generate_pdf(hands_list[0])  # Generate PDF for the first set of hands as an example
