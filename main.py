import random
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image

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
    rank_order = {'2': 16, '3': 15, '4': 14, '5': 13, '6': 12, '7': 11, '8': 10, '9': 9, 'T': 8, 'J': 7, 'Q': 6, 'K': 5,
                  'A': 4, '1': 3, 'Dog': 2, 'Ph': 1, 'Dr': 0}
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
        'North': (10, 730),
        'South': (10, 460),
        'East': (205, 730),
        'West': (205, 460)
    }

    card_width = 38
    card_height = 55
    grid_spacing = 5
    icon_width = 10
    icon_height = 10

    for hand_num, hands in enumerate(hands_list, start=1):
        if hand_num > 1:
            c.showPage()  # Start a new page for each deal

        for player, cards_info in hands.items():
            hand_label = f"Board {hand_num} - {player} - First 8"

            # Create a custom style for bold text
            bold_style = ParagraphStyle(
                'BoldText',
                parent=getSampleStyleSheet()['BodyText'],
                fontName='Helvetica-Bold'
            )

            # Use Paragraph to draw text with custom style
            p = Paragraph(hand_label, style=bold_style)
            p.wrapOn(c, 400, 20)
            p.drawOn(c, player_positions[player][0], player_positions[player][1] + 35)

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
                full_hand_data = [[f"Board {hand_num} - {player} - Full Hand", '']]  # Initialize with column headers

                for suit, cards_in_suit in group_by_suit(cards_info['all_cards']).items():
                    if suit == 'Special':
                        full_hand_data.append(['', ' '.join(cards_in_suit)])
                    else:
                        # Add the suit icon
                        icon_path = f'images/{suit.lower()}_icon.jpg'  # Adjust the path based on your file structure
                        suit_icon = Image(icon_path, width=icon_width, height=icon_height)
                        full_hand_data.append([suit_icon, f"{' '.join(cards_in_suit)}"])

            # Create the table
            full_hand_table = Table(full_hand_data)

            # Style the table
            table_style = [
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center the content vertically
                ('SPAN', (0, 0), (1, 0)),  # Merge the first row
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),  # Center the merged cell content
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),  # Bold the first row
                ('ALIGN', (0, 1), (0, -1), 'RIGHT'),  # Right-align the first column for the rest of the table
                ('TEXTCOLOR', (0, 1), (-1, 1), HexColor('#2d7538')),  # Set text color for the second row (green)
                ('TEXTCOLOR', (0, 2), (-1, 2), HexColor('#0000FF')),  # Set text color for the third row (blue)
                ('TEXTCOLOR', (0, 3), (-1, 3), HexColor('#FF0000')),  # Set text color for the fourth row (red)
                ('TEXTCOLOR', (0, 5), (-1, 5), HexColor('#800080')),  # Set text color for the sixth row (purple)
            ]

            full_hand_table.setStyle(TableStyle(table_style))

            # Position the table on the canvas
            full_hand_table.wrapOn(c, 400, 400)
            full_hand_table.drawOn(c, player_positions[player][0], image_offset_y - 65)

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
