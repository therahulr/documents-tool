"""
Payment and remittance advice generator.

Generates payment advice documents showing payment details,
invoice references, and line item breakdowns.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from .base import BaseDocumentGenerator


class PaymentAdviceGenerator(BaseDocumentGenerator):
    """
    Generates payment/remittance advice documents.
    """

    def get_document_type(self) -> str:
        return 'payment_advice'

    def get_supported_formats(self) -> list:
        return ['pdf', 'docx', 'xlsx', 'odt']

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate a payment advice document.

        Returns:
            dict: Complete payment advice data
        """
        # Payer (the one making payment)
        payer_person = self.data_generator.generate_person()
        payer_address = self.data_generator.generate_address()
        payer_company = self.data_generator.fake.company()

        # Payee (the one receiving payment)
        payee_person = self.data_generator.generate_person()
        payee_address = self.data_generator.generate_address()
        payee_company = self.data_generator.fake.company()

        # Payment details
        payment_date = datetime.now()
        settlement_date = payment_date + timedelta(days=random.randint(1, 3))

        payment_method = random.choice([
            'Wire Transfer',
            'ACH Transfer',
            'Check',
            'Electronic Payment',
        ])

        # Invoice references
        num_invoices = random.randint(1, 5)
        invoices = []

        for _ in range(num_invoices):
            invoice_num = self.data_generator.generate_invoice_number()
            invoice_date = payment_date - timedelta(days=random.randint(10, 60))

            # Generate line items for this invoice
            line_items = self.data_generator.generate_line_items(
                num_items=random.randint(1, 6)
            )

            subtotal = sum(item['total'] for item in line_items)

            # Tax
            tax_rate = random.choice([0.0, 0.05, 0.0625, 0.07, 0.0825, 0.10])
            tax_amount = round(subtotal * tax_rate, 2)

            # Discount (sometimes)
            discount_rate = random.choice([0.0, 0.0, 0.0, 0.05, 0.10])
            discount_amount = round(subtotal * discount_rate, 2)

            # Total
            total = round(subtotal - discount_amount + tax_amount, 2)

            invoices.append({
                'invoice_number': invoice_num,
                'invoice_date': invoice_date,
                'line_items': line_items,
                'subtotal': subtotal,
                'discount_rate': discount_rate,
                'discount_amount': discount_amount,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total': total,
            })

        # Payment total
        payment_total = sum(inv['total'] for inv in invoices)

        # Reference number
        reference_number = self.data_generator.generate_reference_number()

        content = {
            'reference_number': reference_number,
            'payment_date': payment_date,
            'settlement_date': settlement_date,
            'payment_method': payment_method,
            'payer': {
                'name': payer_company,
                'contact': payer_person['full_name'],
                'email': payer_person['email'],
                'phone': payer_person['phone'],
                'address': payer_address,
            },
            'payee': {
                'name': payee_company,
                'contact': payee_person['full_name'],
                'email': payee_person['email'],
                'phone': payee_person['phone'],
                'address': payee_address,
            },
            'invoices': invoices,
            'payment_total': round(payment_total, 2),
            'currency': 'USD',
            'bank_details': {
                'bank_name': self.data_generator.generate_bank_name(),
                'account_number': self.data_generator.generate_account_number(),
                'routing_number': self.data_generator.generate_routing_number(),
            },
            'notes': random.choice([
                'Thank you for your business.',
                'Payment processed as agreed.',
                'All invoices paid in full.',
                '',
            ]),
        }

        return content

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics for size calculation.

        Args:
            content: Payment advice content

        Returns:
            dict: Metrics for size estimation
        """
        num_invoices = len(content['invoices'])
        total_line_items = sum(len(inv['line_items']) for inv in content['invoices'])

        # Estimate pages
        num_pages = max(1, (total_line_items // 20) + 1)

        # Estimate characters
        total_chars = 800  # Header and summary
        total_chars += total_line_items * 60  # Each line item

        # For XLSX
        num_rows = total_line_items + (num_invoices * 2) + 5  # Items + invoice headers + summary

        return {
            'num_pages': num_pages,
            'total_chars': total_chars,
            'num_table_rows': total_line_items + num_invoices,
            'num_paragraphs': num_pages * 2,
            'num_rows': num_rows,
            'num_cols': 5,  # Description, Quantity, Unit Price, Total, etc.
        }
