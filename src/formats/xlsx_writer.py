"""
XLSX format writer.

Generates Excel spreadsheets from content data using openpyxl.
"""

from datetime import datetime
from typing import Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from ..utils.watermark import get_watermark_text
from ..utils.formatting import format_currency, format_date


class XLSXWriter:
    """
    Writes documents to XLSX format with watermarking.
    """

    def __init__(self, filepath: str):
        """
        Initialize XLSX writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath
        self.watermark_text = get_watermark_text()

    def write(self, content: Dict[str, Any], doc_type: str):
        """
        Write content to XLSX file.

        Args:
            content: Document content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        wb = Workbook()
        ws = wb.active

        # Add watermark row
        self._add_watermark(ws)

        # Dispatch to specific handler
        handlers = {
            'bank_statement': self._write_bank_statement,
            'credit_card_statement': self._write_credit_card_statement,
            'payment_advice': self._write_payment_advice,
        }

        handler = handlers.get(doc_type)
        if handler:
            handler(ws, content)
        else:
            raise ValueError(f"Unsupported document type for XLSX: {doc_type}")

        wb.save(self.filepath)
        return self.filepath

    def _add_watermark(self, ws):
        """Add watermark to first row of worksheet."""
        # Merge cells for watermark
        ws.merge_cells('A1:F1')
        cell = ws['A1']
        cell.value = self.watermark_text
        cell.font = Font(bold=True, size=11, color='856404')
        cell.fill = PatternFill(start_color='FFF3CD', end_color='FFF3CD', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 25

    def _write_bank_statement(self, ws, content: Dict[str, Any]):
        """Write bank statement to XLSX."""
        ws.title = 'Bank Statement'

        row = 3  # Start after watermark

        # Title
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = content['bank_name']
        ws[f'A{row}'].font = Font(bold=True, size=14, color='0066CC')
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        row += 1

        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = 'Account Statement'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        row += 2

        # Account info
        info_data = [
            ['Account Holder:', content['customer']['full_name']],
            ['Account Number:', f"****{content['account_number'][-4:]}"],
            ['Account Type:', content['account_type']],
            ['Statement Period:', f"{format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}"],
        ]

        for label, value in info_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'] = value
            row += 1

        row += 1

        # Summary
        ws[f'A{row}'] = 'Account Summary'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1

        summary_data = [
            ['Opening Balance:', content['opening_balance']],
            ['Total Deposits:', content['summary']['total_deposits']],
            ['Total Withdrawals:', content['summary']['total_withdrawals']],
            ['Fees Charged:', content['summary']['total_fees']],
            ['Interest Earned:', content['summary']['interest_earned']],
            ['Closing Balance:', content['closing_balance']],
        ]

        for label, value in summary_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'] = format_currency(value)
            ws[f'B{row}'].alignment = Alignment(horizontal='right')
            row += 1

        # Highlight closing balance
        ws[f'A{row-1}'].fill = PatternFill(start_color='FFF3CD', end_color='FFF3CD', fill_type='solid')
        ws[f'B{row-1}'].fill = PatternFill(start_color='FFF3CD', end_color='FFF3CD', fill_type='solid')
        ws[f'B{row-1}'].font = Font(bold=True)

        row += 2

        # Transactions
        ws[f'A{row}'] = 'Transaction History'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1

        # Transaction table header
        headers = ['Date', 'Description', 'Amount', 'Balance']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='808080', end_color='808080', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')

        row += 1

        # Transaction data
        for trans in content['transactions']:
            ws[f'A{row}'] = format_date(trans['date'])
            ws[f'B{row}'] = trans['description'][:80]
            ws[f'C{row}'] = format_currency(trans['amount'])
            ws[f'D{row}'] = format_currency(trans['balance'])

            ws[f'C{row}'].alignment = Alignment(horizontal='right')
            ws[f'D{row}'].alignment = Alignment(horizontal='right')

            # Alternate row colors
            if row % 2 == 0:
                for col in range(1, 5):
                    ws.cell(row=row, column=col).fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

            row += 1

        # Auto-size columns
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15

    def _write_credit_card_statement(self, ws, content: Dict[str, Any]):
        """Write credit card statement to XLSX."""
        ws.title = 'Credit Card Statement'

        row = 3

        # Title
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = f"{content['bank_name']} - {content['card_type']} Card"
        ws[f'A{row}'].font = Font(bold=True, size=14, color='0066CC')
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        row += 2

        # Account info
        info_data = [
            ['Cardholder:', content['customer']['full_name']],
            ['Card Number:', f"**** **** **** {content['card_number'][-4:]}"],
            ['Statement Period:', f"{format_date(content['statement_period']['start'])} - {format_date(content['statement_period']['end'])}"],
            ['Payment Due Date:', format_date(content['due_date'])],
        ]

        for label, value in info_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'] = value
            row += 1

        row += 1

        # Payment summary
        ws[f'A{row}'] = 'Payment Information'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1

        payment_data = [
            ['Previous Balance:', content['summary']['previous_balance']],
            ['Payments:', -content['summary']['total_payments']],
            ['Purchases:', content['summary']['total_purchases']],
            ['Interest Charged:', content['summary']['interest_charged']],
            ['Fees:', content['summary']['fees_charged']],
            ['New Balance:', content['summary']['new_balance']],
            ['Minimum Payment Due:', content['summary']['minimum_payment']],
        ]

        for label, value in payment_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'] = format_currency(value)
            ws[f'B{row}'].alignment = Alignment(horizontal='right')

            # Highlight important rows
            if 'New Balance' in label or 'Minimum Payment' in label:
                ws[f'A{row}'].fill = PatternFill(start_color='FFF3CD', end_color='FFF3CD', fill_type='solid')
                ws[f'B{row}'].fill = PatternFill(start_color='FFF3CD', end_color='FFF3CD', fill_type='solid')
                ws[f'B{row}'].font = Font(bold=True)

            row += 1

        row += 2

        # Transactions
        ws[f'A{row}'] = 'Purchases and Adjustments'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1

        # Header
        headers = ['Date', 'Merchant', 'Location', 'Amount']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='808080', end_color='808080', fill_type='solid')

        row += 1

        # Data
        for purchase in content['purchases']:
            ws[f'A{row}'] = format_date(purchase['date'])
            ws[f'B{row}'] = purchase['merchant'][:50]
            ws[f'C{row}'] = purchase['location']
            ws[f'D{row}'] = format_currency(purchase['amount'])
            ws[f'D{row}'].alignment = Alignment(horizontal='right')

            if row % 2 == 0:
                for col in range(1, 5):
                    ws.cell(row=row, column=col).fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

            row += 1

        # Auto-size columns
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 15

    def _write_payment_advice(self, ws, content: Dict[str, Any]):
        """Write payment advice to XLSX."""
        ws.title = 'Payment Advice'

        row = 3

        # Title
        ws.merge_cells(f'A{row}:E{row}')
        ws[f'A{row}'] = 'Payment Remittance Advice'
        ws[f'A{row}'].font = Font(bold=True, size=14)
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        row += 2

        # Payment info
        info_data = [
            ['Reference Number:', content['reference_number']],
            ['Payment Date:', format_date(content['payment_date'])],
            ['Settlement Date:', format_date(content['settlement_date'])],
            ['Payment Method:', content['payment_method']],
            ['Total Amount:', format_currency(content['payment_total'])],
        ]

        for label, value in info_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'] = value
            row += 1

        row += 2

        # Invoice details
        ws[f'A{row}'] = 'Invoice Details'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1

        for invoice in content['invoices']:
            ws[f'A{row}'] = f"Invoice: {invoice['invoice_number']} (Date: {format_date(invoice['invoice_date'])})"
            ws[f'A{row}'].font = Font(bold=True)
            row += 1

            # Header
            headers = ['Description', 'Qty', 'Unit Price', 'Total']
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')

            row += 1

            # Line items
            for item in invoice['line_items']:
                ws[f'A{row}'] = item['description']
                ws[f'B{row}'] = item['quantity']
                ws[f'C{row}'] = format_currency(item['unit_price'])
                ws[f'D{row}'] = format_currency(item['total'])

                ws[f'B{row}'].alignment = Alignment(horizontal='right')
                ws[f'C{row}'].alignment = Alignment(horizontal='right')
                ws[f'D{row}'].alignment = Alignment(horizontal='right')
                row += 1

            # Summary
            ws[f'C{row}'] = 'Subtotal:'
            ws[f'C{row}'].font = Font(bold=True)
            ws[f'D{row}'] = format_currency(invoice['subtotal'])
            ws[f'D{row}'].alignment = Alignment(horizontal='right')
            row += 1

            if invoice['discount_amount'] > 0:
                ws[f'C{row}'] = f"Discount ({invoice['discount_rate']*100:.0f}%):"
                ws[f'D{row}'] = format_currency(-invoice['discount_amount'])
                ws[f'D{row}'].alignment = Alignment(horizontal='right')
                row += 1

            if invoice['tax_amount'] > 0:
                ws[f'C{row}'] = f"Tax ({invoice['tax_rate']*100:.2f}%):"
                ws[f'D{row}'] = format_currency(invoice['tax_amount'])
                ws[f'D{row}'].alignment = Alignment(horizontal='right')
                row += 1

            ws[f'C{row}'] = 'Total:'
            ws[f'C{row}'].font = Font(bold=True)
            ws[f'D{row}'] = format_currency(invoice['total'])
            ws[f'D{row}'].font = Font(bold=True)
            ws[f'D{row}'].alignment = Alignment(horizontal='right')
            row += 2

        # Auto-size columns
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 10
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
