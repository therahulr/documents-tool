"""
DOCX format writer.

Generates Microsoft Word documents from content data using python-docx.
"""

from datetime import datetime
from typing import Dict, Any
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..utils.watermark import get_watermark_text
from ..utils.formatting import (
    format_currency, format_date, format_date_long,
    format_card_number, format_account_number
)


class DOCXWriter:
    """
    Writes documents to DOCX format with watermarking.
    """

    def __init__(self, filepath: str):
        """
        Initialize DOCX writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath
        self.watermark_text = get_watermark_text()

    def write(self, content: Dict[str, Any], doc_type: str):
        """
        Write content to DOCX file.

        Args:
            content: Document content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        doc = Document()

        # Add watermark header
        self._add_watermark_header(doc)

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
            raise ValueError(f"Unsupported document type for DOCX: {doc_type}")

        doc.save(self.filepath)
        return self.filepath

    def _add_watermark_header(self, doc: Document):
        """Add watermark to document header."""
        section = doc.sections[0]
        header = section.header

        # Add watermark paragraph
        watermark = header.paragraphs[0]
        watermark.text = self.watermark_text
        watermark.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Style the watermark
        run = watermark.runs[0]
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = RGBColor(133, 100, 4)  # Dark brown

        # Add background color effect (by adding a paragraph with shading)
        watermark.paragraph_format.line_spacing = 1.0
        watermark.paragraph_format.space_after = Pt(6)

    def _write_bank_statement(self, doc: Document, content: Dict[str, Any]):
        """Write bank statement to DOCX."""
        # Title
        title = doc.add_heading(content['bank_name'], 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle = doc.add_heading('Account Statement', level=2)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()

        # Account information
        doc.add_heading('Account Information', level=2)
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Light Grid Accent 1'

        info_data = [
            ['Account Holder:', content['customer']['full_name']],
            ['Account Number:', format_account_number(content['account_number'], mask=True)],
            ['Account Type:', content['account_type']],
            ['Statement Period:', f"{format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}"],
        ]

        for i, (label, value) in enumerate(info_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].font.bold = True

        doc.add_paragraph()

        # Summary
        doc.add_heading('Account Summary', level=2)
        summary_table = doc.add_table(rows=6, cols=2)
        summary_table.style = 'Light Grid Accent 1'

        summary_data = [
            ['Opening Balance:', format_currency(content['opening_balance'])],
            ['Total Deposits:', format_currency(content['summary']['total_deposits'])],
            ['Total Withdrawals:', format_currency(content['summary']['total_withdrawals'])],
            ['Fees Charged:', format_currency(content['summary']['total_fees'])],
            ['Interest Earned:', format_currency(content['summary']['interest_earned'])],
            ['Closing Balance:', format_currency(content['closing_balance'])],
        ]

        for i, (label, value) in enumerate(summary_data):
            row = summary_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            # Right-align values
            row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Highlight closing balance
        last_row = summary_table.rows[-1]
        for cell in last_row.cells:
            cell.paragraphs[0].runs[0].font.bold = True

        doc.add_paragraph()

        # Transactions
        doc.add_heading('Transaction History', level=2)

        if content['transactions']:
            trans_table = doc.add_table(rows=len(content['transactions']) + 1, cols=4)
            trans_table.style = 'Light Grid Accent 1'

            # Header
            header_cells = trans_table.rows[0].cells
            headers = ['Date', 'Description', 'Amount', 'Balance']
            for i, header in enumerate(headers):
                header_cells[i].text = header
                header_cells[i].paragraphs[0].runs[0].font.bold = True

            # Data rows
            for i, trans in enumerate(content['transactions'], start=1):
                row = trans_table.rows[i]
                row.cells[0].text = format_date(trans['date'])
                row.cells[1].text = trans['description'][:80]
                row.cells[2].text = format_currency(trans['amount'])
                row.cells[3].text = format_currency(trans['balance'])

                # Right-align amounts
                row.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                row.cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Contact information
        doc.add_paragraph()
        contact = doc.add_paragraph()
        contact.add_run('Questions? ').bold = True
        contact.add_run(f"Contact us at {content['contact_info']['phone']} or visit {content['contact_info']['website']}")

    def _write_credit_card_statement(self, doc: Document, content: Dict[str, Any]):
        """Write credit card statement to DOCX."""
        # Title
        title = doc.add_heading(f"{content['bank_name']} - {content['card_type']} Card", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle = doc.add_heading('Credit Card Statement', level=2)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()

        # Account info
        doc.add_heading('Account Information', level=2)
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Light Grid Accent 1'

        info_data = [
            ['Cardholder:', content['customer']['full_name']],
            ['Card Number:', format_card_number(content['card_number'])],
            ['Statement Period:', f"{format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}"],
            ['Payment Due Date:', format_date(content['due_date'])],
        ]

        for i, (label, value) in enumerate(info_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].font.bold = True

        doc.add_paragraph()

        # Payment summary
        doc.add_heading('Payment Information', level=2)
        payment_table = doc.add_table(rows=7, cols=2)
        payment_table.style = 'Light Grid Accent 1'

        payment_data = [
            ['Previous Balance:', format_currency(content['summary']['previous_balance'])],
            ['Payments:', format_currency(-content['summary']['total_payments'])],
            ['Purchases:', format_currency(content['summary']['total_purchases'])],
            ['Interest Charged:', format_currency(content['summary']['interest_charged'])],
            ['Fees:', format_currency(content['summary']['fees_charged'])],
            ['New Balance:', format_currency(content['summary']['new_balance'])],
            ['Minimum Payment Due:', format_currency(content['summary']['minimum_payment'])],
        ]

        for i, (label, value) in enumerate(payment_data):
            row = payment_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Highlight important rows
        for idx in [-2, -1]:
            for cell in payment_table.rows[idx].cells:
                cell.paragraphs[0].runs[0].font.bold = True

        doc.add_paragraph()

        # Transactions
        doc.add_heading('Purchases and Adjustments', level=2)

        if content['purchases']:
            trans_table = doc.add_table(rows=len(content['purchases']) + 1, cols=4)
            trans_table.style = 'Light Grid Accent 1'

            # Header
            header_cells = trans_table.rows[0].cells
            headers = ['Date', 'Merchant', 'Location', 'Amount']
            for i, header in enumerate(headers):
                header_cells[i].text = header
                header_cells[i].paragraphs[0].runs[0].font.bold = True

            # Data
            for i, purchase in enumerate(content['purchases'], start=1):
                row = trans_table.rows[i]
                row.cells[0].text = format_date(purchase['date'])
                row.cells[1].text = purchase['merchant'][:50]
                row.cells[2].text = purchase['location']
                row.cells[3].text = format_currency(purchase['amount'])
                row.cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def _write_terms_conditions(self, doc: Document, content: Dict[str, Any]):
        """Write terms and conditions to DOCX."""
        # Title
        title = doc.add_heading(content['title'], 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Metadata
        meta = doc.add_paragraph()
        meta.add_run(f"Effective Date: {format_date_long(content['effective_date'])}\n")
        meta.add_run(f"Version: {content['version']}")
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()

        # Sections
        for section in content['sections']:
            doc.add_heading(section['title'], level=2)

            # Split content into paragraphs
            paragraphs = [p.strip() for p in section['content'].split('\n') if p.strip()]
            for para_text in paragraphs:
                doc.add_paragraph(para_text)

        # Footer information
        doc.add_paragraph()
        footer_para = doc.add_paragraph()
        footer_para.add_run(f"Document ID: {content['footer']['document_id']}\n").font.size = Pt(9)
        footer_para.add_run(f"Contact: {content['footer']['contact_email']} | {content['footer']['contact_phone']}").font.size = Pt(9)

    def _write_notification(self, doc: Document, content: Dict[str, Any]):
        """Write notification letter to DOCX."""
        # Sender info (right-aligned)
        sender = doc.add_paragraph()
        sender.add_run(f"{content['bank_name']}\n")
        sender.add_run(f"{content['sender']['department']}\n")
        sender.add_run(f"{content['sender']['address']['street']}\n")
        sender.add_run(f"{content['sender']['address']['city']}, {content['sender']['address']['state']} {content['sender']['address']['zip_code']}")
        sender.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        doc.add_paragraph()

        # Date
        date_para = doc.add_paragraph(format_date_long(content['date']))

        doc.add_paragraph()

        # Recipient
        recip = doc.add_paragraph()
        recip.add_run(f"{content['customer']['full_name']}\n")
        recip.add_run(f"{content['customer']['street']}\n")
        recip.add_run(f"{content['customer']['city']}, {content['customer']['state']} {content['customer']['zip_code']}")

        doc.add_paragraph()

        # Subject line
        subject = doc.add_paragraph()
        subject.add_run('RE: ').bold = True
        subject.add_run(content['subject'])

        ref = doc.add_paragraph()
        ref.add_run('Reference Number: ').bold = True
        ref.add_run(content['reference_number'])

        doc.add_paragraph()

        # Body
        paragraphs = [p.strip() for p in content['body'].split('\n\n') if p.strip()]
        for para_text in paragraphs:
            doc.add_paragraph(para_text)

    def _write_payment_advice(self, doc: Document, content: Dict[str, Any]):
        """Write payment advice to DOCX."""
        # Title
        title = doc.add_heading('Payment Remittance Advice', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()

        # Payment info
        doc.add_heading('Payment Information', level=2)
        info_table = doc.add_table(rows=5, cols=2)
        info_table.style = 'Light Grid Accent 1'

        info_data = [
            ['Reference Number:', content['reference_number']],
            ['Payment Date:', format_date(content['payment_date'])],
            ['Settlement Date:', format_date(content['settlement_date'])],
            ['Payment Method:', content['payment_method']],
            ['Total Amount:', format_currency(content['payment_total'])],
        ]

        for i, (label, value) in enumerate(info_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].font.bold = True

        doc.add_paragraph()

        # Parties
        doc.add_heading('Parties', level=2)
        party_table = doc.add_table(rows=6, cols=2)
        party_table.style = 'Light Grid Accent 1'

        # Headers
        party_table.rows[0].cells[0].text = 'From (Payer)'
        party_table.rows[0].cells[1].text = 'To (Payee)'
        for cell in party_table.rows[0].cells:
            cell.paragraphs[0].runs[0].font.bold = True

        # Data
        party_data = [
            [content['payer']['name'], content['payee']['name']],
            [content['payer']['contact'], content['payee']['contact']],
            [content['payer']['address']['street'], content['payee']['address']['street']],
            [f"{content['payer']['address']['city']}, {content['payer']['address']['state']} {content['payer']['address']['zip_code']}",
             f"{content['payee']['address']['city']}, {content['payee']['address']['state']} {content['payee']['address']['zip_code']}"],
            [content['payer']['email'], content['payee']['email']],
        ]

        for i, (payer_val, payee_val) in enumerate(party_data, start=1):
            party_table.rows[i].cells[0].text = payer_val
            party_table.rows[i].cells[1].text = payee_val

        doc.add_paragraph()

        # Invoice details
        doc.add_heading('Invoice Details', level=2)

        for invoice in content['invoices']:
            doc.add_heading(f"Invoice: {invoice['invoice_number']} (Date: {format_date(invoice['invoice_date'])})", level=3)

            # Line items
            item_table = doc.add_table(rows=len(invoice['line_items']) + 5, cols=4)
            item_table.style = 'Light Grid Accent 1'

            # Header
            headers = ['Description', 'Qty', 'Unit Price', 'Total']
            for i, header in enumerate(headers):
                item_table.rows[0].cells[i].text = header
                item_table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

            # Items
            row_idx = 1
            for item in invoice['line_items']:
                row = item_table.rows[row_idx]
                row.cells[0].text = item['description']
                row.cells[1].text = str(item['quantity'])
                row.cells[2].text = format_currency(item['unit_price'])
                row.cells[3].text = format_currency(item['total'])
                row_idx += 1

            # Summary rows
            summary_rows = [
                ('Subtotal:', format_currency(invoice['subtotal'])),
            ]
            if invoice['discount_amount'] > 0:
                summary_rows.append((f"Discount ({invoice['discount_rate']*100:.0f}%):", format_currency(-invoice['discount_amount'])))
            if invoice['tax_amount'] > 0:
                summary_rows.append((f"Tax ({invoice['tax_rate']*100:.2f}%):", format_currency(invoice['tax_amount'])))
            summary_rows.append(('Total:', format_currency(invoice['total'])))

            for label, value in summary_rows:
                row = item_table.rows[row_idx]
                row.cells[2].text = label
                row.cells[3].text = value
                row.cells[2].paragraphs[0].runs[0].font.bold = True
                row.cells[3].paragraphs[0].runs[0].font.bold = True
                row_idx += 1

            doc.add_paragraph()
