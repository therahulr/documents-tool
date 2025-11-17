"""
Image format writer (JPEG/PNG).

Generates image-based documents from content data using Pillow.
"""

from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
import textwrap

from src.utils.watermark import get_watermark_text
from src.utils.formatting import format_currency, format_date, format_account_number, format_card_number


class ImageWriter:
    """
    Writes documents to image formats (JPEG/PNG) with watermarking.
    """

    def __init__(self, filepath: str):
        """
        Initialize image writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath
        self.watermark_text = get_watermark_text()

        # Image settings
        self.width = 850
        self.height = 1100  # US Letter aspect ratio
        self.bg_color = (255, 255, 255)  # White
        self.text_color = (0, 0, 0)  # Black
        self.watermark_bg = (255, 243, 205)  # Light yellow
        self.watermark_text_color = (133, 100, 4)  # Dark brown
        self.line_height = 20
        self.margin = 40

    def write(self, content: Dict[str, Any], doc_type: str):
        """
        Write content to image file.

        Args:
            content: Document content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        # Create image
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Try to load better fonts, fall back to default
        try:
            font_regular = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_heading = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            # Fallback to default font
            font_regular = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_heading = ImageFont.load_default()

        # Add watermark banner
        draw.rectangle([(0, 0), (self.width, 30)], fill=self.watermark_bg)
        # Center the watermark text
        bbox = draw.textbbox((0, 0), self.watermark_text, font=font_bold)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) / 2
        draw.text((x, 8), self.watermark_text, fill=self.watermark_text_color, font=font_bold)

        # Dispatch to specific handler
        handlers = {
            'bank_statement': self._draw_bank_statement,
            'credit_card_statement': self._draw_credit_card_statement,
            'notification': self._draw_notification,
        }

        handler = handlers.get(doc_type)
        if handler:
            handler(draw, content, font_regular, font_bold, font_title, font_heading)
        else:
            # Generic text rendering
            self._draw_generic(draw, content, font_regular, font_bold, font_title)

        # Save image
        # Determine format from extension
        if self.filepath.lower().endswith('.png'):
            img.save(self.filepath, 'PNG')
        elif self.filepath.lower().endswith(('.jpg', '.jpeg')):
            img.save(self.filepath, 'JPEG', quality=90)
        else:
            img.save(self.filepath)

        return self.filepath

    def _draw_bank_statement(self, draw, content, font_regular, font_bold, font_title, font_heading):
        """Draw bank statement on image."""
        y = 50  # Start below watermark

        # Title
        title = content['bank_name']
        bbox = draw.textbbox((0, 0), title, font=font_title)
        text_width = bbox[2] - bbox[0]
        draw.text(((self.width - text_width) / 2, y), title, fill=(0, 102, 204), font=font_title)
        y += 30

        subtitle = "Account Statement"
        bbox = draw.textbbox((0, 0), subtitle, font=font_heading)
        text_width = bbox[2] - bbox[0]
        draw.text(((self.width - text_width) / 2, y), subtitle, fill=self.text_color, font=font_heading)
        y += 40

        # Account info
        draw.text((self.margin, y), "Account Information", fill=self.text_color, font=font_heading)
        y += 25

        info_lines = [
            f"Account Holder: {content['customer']['full_name']}",
            f"Account Number: {format_account_number(content['account_number'], mask=True)}",
            f"Account Type: {content['account_type']}",
            f"Period: {format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}",
        ]

        for line in info_lines:
            draw.text((self.margin, y), line, fill=self.text_color, font=font_regular)
            y += self.line_height

        y += 20

        # Summary
        draw.text((self.margin, y), "Account Summary", fill=self.text_color, font=font_heading)
        y += 25

        # Draw summary box
        box_x = self.margin
        box_width = 400
        box_height = 140
        draw.rectangle([(box_x, y), (box_x + box_width, y + box_height)],
                      outline=self.text_color, width=1)

        summary_lines = [
            f"Opening Balance: {format_currency(content['opening_balance'])}",
            f"Total Deposits: {format_currency(content['summary']['total_deposits'])}",
            f"Total Withdrawals: {format_currency(content['summary']['total_withdrawals'])}",
            f"Fees Charged: {format_currency(content['summary']['total_fees'])}",
            f"Interest Earned: {format_currency(content['summary']['interest_earned'])}",
            f"Closing Balance: {format_currency(content['closing_balance'])}",
        ]

        y_box = y + 10
        for i, line in enumerate(summary_lines):
            if i == len(summary_lines) - 1:  # Last line (closing balance)
                draw.text((box_x + 10, y_box), line, fill=self.text_color, font=font_bold)
            else:
                draw.text((box_x + 10, y_box), line, fill=self.text_color, font=font_regular)
            y_box += self.line_height

        y += box_height + 30

        # Recent transactions header
        draw.text((self.margin, y), "Recent Transactions", fill=self.text_color, font=font_heading)
        y += 25

        # Transaction table header
        draw.text((self.margin, y), "Date", fill=self.text_color, font=font_bold)
        draw.text((self.margin + 100, y), "Description", fill=self.text_color, font=font_bold)
        draw.text((self.margin + 450, y), "Amount", fill=self.text_color, font=font_bold)
        draw.text((self.margin + 600, y), "Balance", fill=self.text_color, font=font_bold)
        y += 20

        # Draw line
        draw.line([(self.margin, y), (self.width - self.margin, y)], fill=self.text_color, width=1)
        y += 5

        # Show first 20 transactions
        for trans in content['transactions'][:20]:
            if y > self.height - 50:  # Near bottom of image
                break

            date_str = format_date(trans['date'])
            desc = trans['description'][:35]  # Truncate long descriptions
            amount = format_currency(trans['amount'])
            balance = format_currency(trans['balance'])

            draw.text((self.margin, y), date_str, fill=self.text_color, font=font_regular)
            draw.text((self.margin + 100, y), desc, fill=self.text_color, font=font_regular)
            draw.text((self.margin + 450, y), amount, fill=self.text_color, font=font_regular)
            draw.text((self.margin + 600, y), balance, fill=self.text_color, font=font_regular)
            y += self.line_height

        # Contact info at bottom
        if y < self.height - 40:
            y = self.height - 40
            contact = f"Questions? {content['contact_info']['phone']} | {content['contact_info']['website']}"
            draw.text((self.margin, y), contact, fill=self.text_color, font=font_regular)

    def _draw_credit_card_statement(self, draw, content, font_regular, font_bold, font_title, font_heading):
        """Draw credit card statement on image."""
        y = 50

        # Title
        title = f"{content['bank_name']} - {content['card_type']} Card"
        bbox = draw.textbbox((0, 0), title, font=font_title)
        text_width = bbox[2] - bbox[0]
        draw.text(((self.width - text_width) / 2, y), title, fill=(0, 102, 204), font=font_title)
        y += 30

        subtitle = "Credit Card Statement"
        bbox = draw.textbbox((0, 0), subtitle, font=font_heading)
        text_width = bbox[2] - bbox[0]
        draw.text(((self.width - text_width) / 2, y), subtitle, fill=self.text_color, font=font_heading)
        y += 40

        # Account info
        info_lines = [
            f"Cardholder: {content['customer']['full_name']}",
            f"Card Number: {format_card_number(content['card_number'])}",
            f"Due Date: {format_date(content['due_date'])}",
        ]

        for line in info_lines:
            draw.text((self.margin, y), line, fill=self.text_color, font=font_regular)
            y += self.line_height

        y += 20

        # Payment summary box
        draw.text((self.margin, y), "Payment Information", fill=self.text_color, font=font_heading)
        y += 25

        box_x = self.margin
        box_width = 450
        box_height = 180
        draw.rectangle([(box_x, y), (box_x + box_width, y + box_height)],
                      fill=(255, 250, 240), outline=self.text_color, width=2)

        y_box = y + 10
        payment_lines = [
            f"Previous Balance: {format_currency(content['summary']['previous_balance'])}",
            f"Payments: {format_currency(-content['summary']['total_payments'])}",
            f"Purchases: {format_currency(content['summary']['total_purchases'])}",
            f"Interest: {format_currency(content['summary']['interest_charged'])}",
            f"Fees: {format_currency(content['summary']['fees_charged'])}",
            "",
            f"NEW BALANCE: {format_currency(content['summary']['new_balance'])}",
            f"MINIMUM PAYMENT DUE: {format_currency(content['summary']['minimum_payment'])}",
        ]

        for i, line in enumerate(payment_lines):
            if i >= 6:  # Last two lines
                draw.text((box_x + 10, y_box), line, fill=self.text_color, font=font_bold)
            else:
                draw.text((box_x + 10, y_box), line, fill=self.text_color, font=font_regular)
            y_box += self.line_height

        y += box_height + 30

        # Transactions
        draw.text((self.margin, y), "Recent Purchases", fill=self.text_color, font=font_heading)
        y += 25

        # Show first 15 purchases
        for purchase in content['purchases'][:15]:
            if y > self.height - 50:
                break

            line = f"{format_date(purchase['date'])} - {purchase['merchant'][:30]} - {format_currency(purchase['amount'])}"
            draw.text((self.margin, y), line, fill=self.text_color, font=font_regular)
            y += self.line_height

    def _draw_notification(self, draw, content, font_regular, font_bold, font_title, font_heading):
        """Draw notification letter on image."""
        y = 50

        # Sender info (right-aligned)
        sender_lines = [
            content['bank_name'],
            content['sender']['department'],
            content['sender']['address']['street'],
            f"{content['sender']['address']['city']}, {content['sender']['address']['state']} {content['sender']['address']['zip_code']}",
        ]

        for line in sender_lines:
            bbox = draw.textbbox((0, 0), line, font=font_regular)
            text_width = bbox[2] - bbox[0]
            draw.text((self.width - self.margin - text_width, y), line, fill=self.text_color, font=font_regular)
            y += self.line_height

        y += 30

        # Recipient
        recip_lines = [
            content['customer']['full_name'],
            content['customer']['street'],
            f"{content['customer']['city']}, {content['customer']['state']} {content['customer']['zip_code']}",
        ]

        for line in recip_lines:
            draw.text((self.margin, y), line, fill=self.text_color, font=font_regular)
            y += self.line_height

        y += 30

        # Subject
        draw.text((self.margin, y), "RE:", fill=self.text_color, font=font_bold)
        draw.text((self.margin + 30, y), content['subject'][:70], fill=self.text_color, font=font_regular)
        y += 25

        # Body (wrapped)
        body_paragraphs = content['body'].split('\n\n')
        for para in body_paragraphs[:5]:  # Limit paragraphs
            if y > self.height - 100:
                break

            # Wrap text
            wrapped = textwrap.wrap(para, width=90)
            for line in wrapped[:15]:  # Limit lines
                if y > self.height - 50:
                    break
                draw.text((self.margin, y), line, fill=self.text_color, font=font_regular)
                y += self.line_height
            y += 10

    def _draw_generic(self, draw, content, font_regular, font_bold, font_title):
        """Draw generic content as text."""
        y = 50

        # Title if available
        if 'title' in content:
            bbox = draw.textbbox((0, 0), content['title'], font=font_title)
            text_width = bbox[2] - bbox[0]
            draw.text(((self.width - text_width) / 2, y), content['title'], fill=self.text_color, font=font_title)
            y += 40

        # Draw content as text
        content_str = str(content)[:2000]  # Limit length
        wrapped = textwrap.wrap(content_str, width=90)

        for line in wrapped[:50]:  # Limit lines
            if y > self.height - 50:
                break
            draw.text((self.margin, y), line, fill=self.text_color, font=font_regular)
            y += self.line_height
