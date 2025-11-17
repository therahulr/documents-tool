"""
PDF format writer.

Generates PDF documents from content data using reportlab.
"""

from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak
)
from reportlab.pdfgen import canvas

from src.utils.watermark import get_watermark_text
from src.utils.formatting import (
    format_currency, format_date, format_date_long,
    format_card_number, format_account_number, format_address_block
)


class PDFWriter:
    """
    Writes documents to PDF format with watermarking.
    """

    def __init__(self, filepath: str):
        """
        Initialize PDF writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath
        self.watermark_text = get_watermark_text()

    def write(self, content: Dict[str, Any], doc_type: str):
        """
        Write content to PDF file.

        Args:
            content: Document content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        # Dispatch to specific handler based on document type
        handlers = {
            'bank_statement': self._write_bank_statement,
            'credit_card_statement': self._write_credit_card_statement,
            'terms_conditions': self._write_terms_conditions,
            'notification': self._write_notification,
            'payment_advice': self._write_payment_advice,
        }

        handler = handlers.get(doc_type)
        if handler:
            handler(content)
        else:
            raise ValueError(f"Unsupported document type for PDF: {doc_type}")

        return self.filepath

    def _create_pdf_with_watermark(self, build_function):
        """
        Create PDF with watermark on each page.

        Args:
            build_function: Function that builds the PDF content
        """
        doc = SimpleDocTemplate(
            self.filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=inch,
            bottomMargin=0.75*inch,
        )

        # Build the PDF
        story = []
        build_function(story, doc)

        # Add watermark callback
        doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)

    def _add_watermark(self, canvas_obj, doc):
        """
        Add watermark to page - multiple placements for professional documents.

        Args:
            canvas_obj: ReportLab canvas
            doc: Document template
        """
        canvas_obj.saveState()

        # 1. Top banner watermark
        canvas_obj.setFillColor(colors.Color(1, 0.95, 0.8, alpha=0.9))  # Light yellow
        canvas_obj.rect(0, doc.height + doc.topMargin + 10, doc.width + doc.leftMargin + doc.rightMargin, 30, fill=1, stroke=0)

        canvas_obj.setFillColor(colors.Color(0.5, 0.25, 0, alpha=1))  # Dark brown
        canvas_obj.setFont("Helvetica-Bold", 9)

        # Center the watermark text
        text_width = canvas_obj.stringWidth(self.watermark_text, "Helvetica-Bold", 9)
        x = (doc.width + doc.leftMargin + doc.rightMargin - text_width) / 2
        y = doc.height + doc.topMargin + 18

        canvas_obj.drawString(x, y, self.watermark_text)

        # 2. Footer watermark (smaller text)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(colors.Color(0.5, 0.5, 0.5, alpha=0.6))  # Gray
        footer_text_width = canvas_obj.stringWidth(self.watermark_text, "Helvetica", 7)
        footer_x = (doc.width + doc.leftMargin + doc.rightMargin - footer_text_width) / 2
        canvas_obj.drawString(footer_x, 0.3*inch, self.watermark_text)

        # 3. Diagonal watermark in center (rotated, faint)
        canvas_obj.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.15))  # Very light gray
        canvas_obj.setFont("Helvetica-Bold", 48)

        # Rotate and draw diagonal watermark
        canvas_obj.saveState()
        canvas_obj.translate(doc.width/2 + doc.leftMargin, doc.height/2 + doc.bottomMargin)
        canvas_obj.rotate(45)
        diag_text = "TEST DOCUMENT"
        diag_width = canvas_obj.stringWidth(diag_text, "Helvetica-Bold", 48)
        canvas_obj.drawString(-diag_width/2, 0, diag_text)
        canvas_obj.restoreState()

        # 4. Page number at bottom right
        canvas_obj.setFillColor(colors.black)
        canvas_obj.setFont("Helvetica", 9)
        page_num = f"Page {doc.page}"
        canvas_obj.drawString(doc.width - 1*inch, 0.5*inch, page_num)

        canvas_obj.restoreState()

    def _write_bank_statement(self, content: Dict[str, Any]):
        """Write bank statement to PDF."""
        def build(story, doc):
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#0066cc'),
                spaceAfter=12,
            )
            story.append(Paragraph(f"{content['bank_name']}", title_style))
            story.append(Paragraph("Account Statement", title_style))
            story.append(Spacer(1, 0.2*inch))

            # Account info
            account_data = [
                ['Account Holder:', content['customer']['full_name']],
                ['Account Number:', format_account_number(content['account_number'], mask=True)],
                ['Account Type:', content['account_type']],
                ['Statement Period:', f"{format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}"],
            ]

            account_table = Table(account_data, colWidths=[2*inch, 4*inch])
            account_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(account_table)
            story.append(Spacer(1, 0.3*inch))

            # Summary
            story.append(Paragraph("Account Summary", styles['Heading2']))
            summary_data = [
                ['Opening Balance:', format_currency(content['opening_balance'])],
                ['Total Deposits:', format_currency(content['summary']['total_deposits'])],
                ['Total Withdrawals:', format_currency(content['summary']['total_withdrawals'])],
                ['Fees Charged:', format_currency(content['summary']['total_fees'])],
                ['Interest Earned:', format_currency(content['summary']['interest_earned'])],
                ['Closing Balance:', format_currency(content['closing_balance'])],
            ]

            summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))

            # Transactions
            story.append(Paragraph("Transaction History", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))

            trans_data = [['Date', 'Description', 'Amount', 'Balance']]

            for trans in content['transactions']:
                trans_data.append([
                    format_date(trans['date']),
                    Paragraph(trans['description'][:60], styles['Normal']),
                    format_currency(trans['amount']),
                    format_currency(trans['balance']),
                ])

            trans_table = Table(trans_data, colWidths=[1*inch, 3.2*inch, 1*inch, 1*inch])
            trans_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ]))
            story.append(trans_table)

            # Contact info
            story.append(Spacer(1, 0.3*inch))
            contact_text = f"<b>Questions?</b> Contact us at {content['contact_info']['phone']} or visit {content['contact_info']['website']}"
            story.append(Paragraph(contact_text, styles['Normal']))

        self._create_pdf_with_watermark(build)

    def _write_credit_card_statement(self, content: Dict[str, Any]):
        """Write credit card statement to PDF."""
        def build(story, doc):
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0066cc'))
            story.append(Paragraph(f"{content['bank_name']} - {content['card_type']} Card", title_style))
            story.append(Paragraph("Credit Card Statement", title_style))
            story.append(Spacer(1, 0.2*inch))

            # Account info
            info_data = [
                ['Cardholder:', content['customer']['full_name']],
                ['Card Number:', format_card_number(content['card_number'])],
                ['Statement Period:', f"{format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}"],
                ['Payment Due Date:', format_date(content['due_date'])],
            ]
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.2*inch))

            # Payment summary box
            story.append(Paragraph("Payment Information", styles['Heading2']))
            payment_data = [
                ['Previous Balance:', format_currency(content['summary']['previous_balance'])],
                ['Payments:', format_currency(-content['summary']['total_payments'])],
                ['Purchases:', format_currency(content['summary']['total_purchases'])],
                ['Interest Charged:', format_currency(content['summary']['interest_charged'])],
                ['Fees:', format_currency(content['summary']['fees_charged'])],
                ['New Balance:', format_currency(content['summary']['new_balance'])],
                ['Minimum Payment Due:', format_currency(content['summary']['minimum_payment'])],
            ]
            payment_table = Table(payment_data, colWidths=[2.5*inch, 1.5*inch])
            payment_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, -2), (-1, -1), colors.Color(1, 0.95, 0.8)),
                ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ]))
            story.append(payment_table)
            story.append(Spacer(1, 0.3*inch))

            # Transactions
            story.append(Paragraph("Purchases and Adjustments", styles['Heading2']))
            trans_data = [['Date', 'Merchant', 'Location', 'Amount']]

            for purchase in content['purchases']:
                trans_data.append([
                    format_date(purchase['date']),
                    Paragraph(purchase['merchant'][:40], styles['Normal']),
                    purchase['location'],
                    format_currency(purchase['amount']),
                ])

            if trans_data:
                trans_table = Table(trans_data, colWidths=[0.9*inch, 2.3*inch, 1.5*inch, 1*inch])
                trans_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
                ]))
                story.append(trans_table)

        self._create_pdf_with_watermark(build)

    def _write_terms_conditions(self, content: Dict[str, Any]):
        """Write terms and conditions to PDF."""
        def build(story, doc):
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
            story.append(Paragraph(content['title'], title_style))
            story.append(Paragraph(f"Effective Date: {format_date_long(content['effective_date'])}", styles['Normal']))
            story.append(Paragraph(f"Version: {content['version']}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

            # Sections
            for section in content['sections']:
                story.append(Paragraph(section['title'], styles['Heading2']))
                # Split content into paragraphs
                paragraphs = [p.strip() for p in section['content'].split('\n') if p.strip()]
                for para in paragraphs:
                    story.append(Paragraph(para, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                story.append(Spacer(1, 0.2*inch))

            # Footer
            story.append(Spacer(1, 0.3*inch))
            footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
            story.append(Paragraph(f"Document ID: {content['footer']['document_id']}", footer_style))
            story.append(Paragraph(f"Contact: {content['footer']['contact_email']} | {content['footer']['contact_phone']}", footer_style))

        self._create_pdf_with_watermark(build)

    def _write_notification(self, content: Dict[str, Any]):
        """Write notification letter to PDF."""
        def build(story, doc):
            styles = getSampleStyleSheet()

            # Sender info (top right)
            sender_text = f"{content['bank_name']}<br/>{content['sender']['department']}<br/>{content['sender']['address']['street']}<br/>{content['sender']['address']['city']}, {content['sender']['address']['state']} {content['sender']['address']['zip_code']}"
            story.append(Paragraph(sender_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

            # Date
            story.append(Paragraph(format_date_long(content['date']), styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

            # Recipient
            recip_text = f"{content['customer']['full_name']}<br/>{content['customer']['street']}<br/>{content['customer']['city']}, {content['customer']['state']} {content['customer']['zip_code']}"
            story.append(Paragraph(recip_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

            # Reference
            story.append(Paragraph(f"<b>RE:</b> {content['subject']}", styles['Normal']))
            story.append(Paragraph(f"<b>Reference Number:</b> {content['reference_number']}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

            # Body
            paragraphs = [p.strip() for p in content['body'].split('\n\n') if p.strip()]
            for para in paragraphs:
                story.append(Paragraph(para.replace('\n', '<br/>'), styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

        self._create_pdf_with_watermark(build)

    def _write_payment_advice(self, content: Dict[str, Any]):
        """Write payment advice to PDF."""
        def build(story, doc):
            styles = getSampleStyleSheet()

            # Title
            story.append(Paragraph("Payment Remittance Advice", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))

            # Payment info
            info_data = [
                ['Reference Number:', content['reference_number']],
                ['Payment Date:', format_date(content['payment_date'])],
                ['Settlement Date:', format_date(content['settlement_date'])],
                ['Payment Method:', content['payment_method']],
                ['Total Amount:', format_currency(content['payment_total'])],
            ]
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))

            # Payer and Payee
            party_data = [
                ['From (Payer):', 'To (Payee):'],
                [content['payer']['name'], content['payee']['name']],
                [content['payer']['contact'], content['payee']['contact']],
                [content['payer']['address']['street'], content['payee']['address']['street']],
                [f"{content['payer']['address']['city']}, {content['payer']['address']['state']} {content['payer']['address']['zip_code']}",
                 f"{content['payee']['address']['city']}, {content['payee']['address']['state']} {content['payee']['address']['zip_code']}"],
            ]
            party_table = Table(party_data, colWidths=[3*inch, 3*inch])
            party_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(party_table)
            story.append(Spacer(1, 0.3*inch))

            # Invoice details
            story.append(Paragraph("Invoice Details", styles['Heading2']))

            for invoice in content['invoices']:
                story.append(Paragraph(f"Invoice: {invoice['invoice_number']} (Date: {format_date(invoice['invoice_date'])})", styles['Heading3']))

                # Line items
                item_data = [['Description', 'Qty', 'Unit Price', 'Total']]
                for item in invoice['line_items']:
                    item_data.append([
                        item['description'],
                        str(item['quantity']),
                        format_currency(item['unit_price']),
                        format_currency(item['total']),
                    ])

                # Summary rows
                item_data.append(['', '', 'Subtotal:', format_currency(invoice['subtotal'])])
                if invoice['discount_amount'] > 0:
                    item_data.append(['', '', f'Discount ({invoice["discount_rate"]*100:.0f}%):', format_currency(-invoice['discount_amount'])])
                if invoice['tax_amount'] > 0:
                    item_data.append(['', '', f'Tax ({invoice["tax_rate"]*100:.2f}%):', format_currency(invoice['tax_amount'])])
                item_data.append(['', '', 'Total:', format_currency(invoice['total'])])

                item_table = Table(item_data, colWidths=[2.5*inch, 0.6*inch, 1.2*inch, 1*inch])
                item_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -len(invoice['line_items'])-1), 0.5, colors.grey),
                    ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
                    ('LINEABOVE', (2, -1), (-1, -1), 1, colors.black),
                ]))
                story.append(item_table)
                story.append(Spacer(1, 0.2*inch))

        self._create_pdf_with_watermark(build)
