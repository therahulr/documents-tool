"""
ODT format writer.

Generates OpenDocument Text documents from content data using odfpy.
"""

from datetime import datetime
from typing import Dict, Any
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties
from odf.text import P, H, Span
from odf.table import Table, TableColumn, TableRow, TableCell

from src.utils.watermark import get_watermark_text
from src.utils.formatting import (
    format_currency, format_date, format_date_long,
    format_card_number, format_account_number
)


class ODTWriter:
    """
    Writes documents to ODT format with watermarking.
    """

    def __init__(self, filepath: str):
        """
        Initialize ODT writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath
        self.watermark_text = get_watermark_text()

    def write(self, content: Dict[str, Any], doc_type: str):
        """
        Write content to ODT file.

        Args:
            content: Document content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        doc = OpenDocumentText()

        # Define styles
        self._define_styles(doc)

        # Add watermark
        self._add_watermark(doc)

        # Dispatch to specific handler
        handlers = {
            'bank_statement': self._write_bank_statement,
            'credit_card_statement': self._write_credit_card_statement,
            'terms_conditions': self._write_terms_conditions,
            'notification': self._write_notification,
            'payment_advice': self._write_payment_advice,
        }

        handler = handlers.get(doc_type)
        if handler:
            handler(doc, content)
        else:
            raise ValueError(f"Unsupported document type for ODT: {doc_type}")

        doc.save(self.filepath)
        return self.filepath

    def _define_styles(self, doc):
        """Define document styles."""
        # Watermark style
        watermark_style = Style(name="WatermarkStyle", family="paragraph")
        watermark_style.addElement(ParagraphProperties(textalign="center"))
        watermark_style.addElement(TextProperties(fontweight="bold", color="#856404"))
        doc.styles.addElement(watermark_style)

        # Title style
        title_style = Style(name="TitleStyle", family="paragraph")
        title_style.addElement(ParagraphProperties(textalign="center"))
        title_style.addElement(TextProperties(fontsize="18pt", fontweight="bold", color="#0066cc"))
        doc.styles.addElement(title_style)

        # Heading style
        heading_style = Style(name="HeadingStyle", family="paragraph")
        heading_style.addElement(TextProperties(fontsize="14pt", fontweight="bold"))
        doc.styles.addElement(heading_style)

        # Bold style
        bold_style = Style(name="BoldStyle", family="text")
        bold_style.addElement(TextProperties(fontweight="bold"))
        doc.styles.addElement(bold_style)

    def _add_watermark(self, doc):
        """Add watermark paragraph."""
        p = P(stylename="WatermarkStyle")
        p.addText(self.watermark_text)
        doc.text.addElement(p)

        # Add spacing
        doc.text.addElement(P())

    def _write_bank_statement(self, doc, content: Dict[str, Any]):
        """Write bank statement to ODT."""
        # Title
        title = P(stylename="TitleStyle")
        title.addText(content['bank_name'])
        doc.text.addElement(title)

        subtitle = P(stylename="TitleStyle")
        subtitle.addText("Account Statement")
        doc.text.addElement(subtitle)

        doc.text.addElement(P())

        # Account info
        heading = H(outlinelevel=2)
        heading.addText("Account Information")
        doc.text.addElement(heading)

        info_items = [
            f"Account Holder: {content['customer']['full_name']}",
            f"Account Number: {format_account_number(content['account_number'], mask=True)}",
            f"Account Type: {content['account_type']}",
            f"Statement Period: {format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}",
        ]

        for item in info_items:
            doc.text.addElement(P(text=item))

        doc.text.addElement(P())

        # Summary
        heading = H(outlinelevel=2)
        heading.addText("Account Summary")
        doc.text.addElement(heading)

        summary_items = [
            f"Opening Balance: {format_currency(content['opening_balance'])}",
            f"Total Deposits: {format_currency(content['summary']['total_deposits'])}",
            f"Total Withdrawals: {format_currency(content['summary']['total_withdrawals'])}",
            f"Fees Charged: {format_currency(content['summary']['total_fees'])}",
            f"Interest Earned: {format_currency(content['summary']['interest_earned'])}",
            f"Closing Balance: {format_currency(content['closing_balance'])}",
        ]

        for item in summary_items:
            doc.text.addElement(P(text=item))

        doc.text.addElement(P())

        # Transactions
        heading = H(outlinelevel=2)
        heading.addText("Transaction History")
        doc.text.addElement(heading)

        # Create table for transactions
        table = Table()

        # Add columns
        for _ in range(4):
            table.addElement(TableColumn())

        # Header row
        header_row = TableRow()
        for header_text in ['Date', 'Description', 'Amount', 'Balance']:
            cell = TableCell()
            p = P()
            span = Span(stylename="BoldStyle")
            span.addText(header_text)
            p.addElement(span)
            cell.addElement(p)
            header_row.addElement(cell)
        table.addElement(header_row)

        # Data rows
        for trans in content['transactions'][:50]:  # Limit for performance
            row = TableRow()

            # Date
            cell = TableCell()
            cell.addElement(P(text=format_date(trans['date'])))
            row.addElement(cell)

            # Description
            cell = TableCell()
            cell.addElement(P(text=trans['description'][:80]))
            row.addElement(cell)

            # Amount
            cell = TableCell()
            cell.addElement(P(text=format_currency(trans['amount'])))
            row.addElement(cell)

            # Balance
            cell = TableCell()
            cell.addElement(P(text=format_currency(trans['balance'])))
            row.addElement(cell)

            table.addElement(row)

        doc.text.addElement(table)

    def _write_credit_card_statement(self, doc, content: Dict[str, Any]):
        """Write credit card statement to ODT."""
        # Title
        title = P(stylename="TitleStyle")
        title.addText(f"{content['bank_name']} - {content['card_type']} Card")
        doc.text.addElement(title)

        subtitle = P(stylename="TitleStyle")
        subtitle.addText("Credit Card Statement")
        doc.text.addElement(subtitle)

        doc.text.addElement(P())

        # Account info
        heading = H(outlinelevel=2)
        heading.addText("Account Information")
        doc.text.addElement(heading)

        info_items = [
            f"Cardholder: {content['customer']['full_name']}",
            f"Card Number: {format_card_number(content['card_number'])}",
            f"Statement Period: {format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}",
            f"Payment Due Date: {format_date(content['due_date'])}",
        ]

        for item in info_items:
            doc.text.addElement(P(text=item))

        doc.text.addElement(P())

        # Payment summary
        heading = H(outlinelevel=2)
        heading.addText("Payment Information")
        doc.text.addElement(heading)

        summary_items = [
            f"Previous Balance: {format_currency(content['summary']['previous_balance'])}",
            f"Payments: {format_currency(-content['summary']['total_payments'])}",
            f"Purchases: {format_currency(content['summary']['total_purchases'])}",
            f"Interest Charged: {format_currency(content['summary']['interest_charged'])}",
            f"Fees: {format_currency(content['summary']['fees_charged'])}",
            f"New Balance: {format_currency(content['summary']['new_balance'])}",
            f"Minimum Payment Due: {format_currency(content['summary']['minimum_payment'])}",
        ]

        for item in summary_items:
            doc.text.addElement(P(text=item))

        doc.text.addElement(P())

        # Transactions
        heading = H(outlinelevel=2)
        heading.addText("Purchases and Adjustments")
        doc.text.addElement(heading)

        for purchase in content['purchases'][:30]:  # Limit for performance
            p = P()
            p.addText(f"{format_date(purchase['date'])} - {purchase['merchant']} ({purchase['location']}) - {format_currency(purchase['amount'])}")
            doc.text.addElement(p)

    def _write_terms_conditions(self, doc, content: Dict[str, Any]):
        """Write terms and conditions to ODT."""
        # Title
        title = P(stylename="TitleStyle")
        title.addText(content['title'])
        doc.text.addElement(title)

        # Metadata
        meta_text = f"Effective Date: {format_date_long(content['effective_date'])} | Version: {content['version']}"
        doc.text.addElement(P(text=meta_text))

        doc.text.addElement(P())

        # Sections
        for section in content['sections']:
            heading = H(outlinelevel=2)
            heading.addText(section['title'])
            doc.text.addElement(heading)

            # Split content into paragraphs
            paragraphs = [p.strip() for p in section['content'].split('\n') if p.strip()]
            for para_text in paragraphs:
                doc.text.addElement(P(text=para_text))

            doc.text.addElement(P())

    def _write_notification(self, doc, content: Dict[str, Any]):
        """Write notification letter to ODT."""
        # Sender info
        sender_text = f"{content['bank_name']}\n{content['sender']['department']}\n{content['sender']['address']['street']}\n{content['sender']['address']['city']}, {content['sender']['address']['state']} {content['sender']['address']['zip_code']}"
        for line in sender_text.split('\n'):
            doc.text.addElement(P(text=line))

        doc.text.addElement(P())

        # Date
        doc.text.addElement(P(text=format_date_long(content['date'])))

        doc.text.addElement(P())

        # Recipient
        recip_text = f"{content['customer']['full_name']}\n{content['customer']['street']}\n{content['customer']['city']}, {content['customer']['state']} {content['customer']['zip_code']}"
        for line in recip_text.split('\n'):
            doc.text.addElement(P(text=line))

        doc.text.addElement(P())

        # Subject
        p = P()
        span = Span(stylename="BoldStyle")
        span.addText("RE: ")
        p.addElement(span)
        p.addText(content['subject'])
        doc.text.addElement(p)

        p = P()
        span = Span(stylename="BoldStyle")
        span.addText("Reference Number: ")
        p.addElement(span)
        p.addText(content['reference_number'])
        doc.text.addElement(p)

        doc.text.addElement(P())

        # Body
        paragraphs = [p.strip() for p in content['body'].split('\n\n') if p.strip()]
        for para_text in paragraphs:
            doc.text.addElement(P(text=para_text))

    def _write_payment_advice(self, doc, content: Dict[str, Any]):
        """Write payment advice to ODT."""
        # Title
        title = P(stylename="TitleStyle")
        title.addText("Payment Remittance Advice")
        doc.text.addElement(title)

        doc.text.addElement(P())

        # Payment info
        heading = H(outlinelevel=2)
        heading.addText("Payment Information")
        doc.text.addElement(heading)

        info_items = [
            f"Reference Number: {content['reference_number']}",
            f"Payment Date: {format_date(content['payment_date'])}",
            f"Settlement Date: {format_date(content['settlement_date'])}",
            f"Payment Method: {content['payment_method']}",
            f"Total Amount: {format_currency(content['payment_total'])}",
        ]

        for item in info_items:
            doc.text.addElement(P(text=item))

        doc.text.addElement(P())

        # Invoice details
        heading = H(outlinelevel=2)
        heading.addText("Invoice Details")
        doc.text.addElement(heading)

        for invoice in content['invoices']:
            p = P()
            span = Span(stylename="BoldStyle")
            span.addText(f"Invoice: {invoice['invoice_number']} (Date: {format_date(invoice['invoice_date'])})")
            p.addElement(span)
            doc.text.addElement(p)

            for item in invoice['line_items']:
                doc.text.addElement(P(text=f"  {item['description']} - Qty: {item['quantity']} - {format_currency(item['total'])}"))

            doc.text.addElement(P(text=f"  Total: {format_currency(invoice['total'])}"))
            doc.text.addElement(P())
