import random
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

def create_tichu_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['Jade', 'Pagoda', 'Star', 'Sword']
    special_cards = ['1', 'Dog', 'Ph', 'Dr']
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
                  'A': 12, '1': 13, 'Dog': 14, 'Ph': 15, 'Dr': 16}
    suit_order = {'Jade': 0, 'Pagoda': 1, 'Star': 2, 'Sword': 3, 'Special': 4}

    for player, cards_info in hands.items():
        hands[player]['all_cards'] = sorted(cards_info['all_cards'],
                                            key=lambda x: (suit_order[x['suit']], rank_order[x['rank']]))
        hands[player]['first_8_cards'] = sorted(cards_info['first_8_cards'],
                                                key=lambda x: (suit_order[x['suit']], rank_order[x['rank']]))

def group_by_suit(cards):
    grouped_by_suit = {'Jade': [], 'Pagoda': [], 'Star': [], 'Sword': [], 'Special': []}

    for card in cards:
        suit = card['suit']
        rank = card['rank']
        grouped_by_suit[suit].append(f"{rank}")

    return grouped_by_suit


def generate_pdf(hands_list, pdf_filename='tichu_hands.pdf'):
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    player_positions = {
        'North': (20, 750),
        'South': (20, 400),
        'East': (300, 750),
        'West': (300, 400)
    }

    card_width = 40
    card_height = 60
    grid_spacing = 10

    for hand_num, hands in enumerate(hands_list, start=1):
        if hand_num > 1:
            c.showPage()  # Start a new page for each deal

        for player, cards_info in hands.items():
            hand_label = f"Deal {hand_num} - {player}'s hand:"

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

            # Draw images of the first 8 cards
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

            # Display full hand as a 2x5 grid
            full_hand_data = [['Single Column']]
            for suit, cards_in_suit in group_by_suit(cards_info['all_cards']).items():
                full_hand_data.append([suit, ', '.join(cards_in_suit)])

            # Create the table
            full_hand_table = Table(full_hand_data)

            # Style the table
            table_style = [
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center the content vertically
            ]

            full_hand_table.setStyle(TableStyle(table_style))

            # Position the table on the canvas
            full_hand_table.wrapOn(c, 400, 400)
            full_hand_table.drawOn(c, player_positions[player][0], image_offset_y - 100)

    c.save()


if __name__ == "__main__":
    num_deals = 36  # Adjust as needed
    hands_list = []

    for _ in range(num_deals):
        deck = create_tichu_deck()
        hands = deal_cards(deck)
        deal_last_six_cards(deck, hands)
        sort_hands(hands)
        hands_list.append(hands)

    generate_pdf(hands_list)  # Generate PDF for the deals as an example
