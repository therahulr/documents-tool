"""
Notification and letter generator.

Generates various types of banking notifications, alerts, and letters.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from src.generators.base import LetterGenerator
from src.data.templates import DocumentTemplates
from src.utils.formatting import format_currency, format_date


class NotificationGenerator(LetterGenerator):
    """
    Generates notification letters and alerts.
    """

    def get_document_type(self) -> str:
        return 'notification'

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate a notification letter.

        Returns:
            dict: Complete notification data
        """
        # Select notification type
        notification_type = self.config.get('notification_type')
        if notification_type not in DocumentTemplates.NOTIFICATION_TYPES:
            notification_type = random.choice(list(DocumentTemplates.NOTIFICATION_TYPES.keys()))

        # Generate data for template variables
        template_data = self._generate_template_data(notification_type)

        # Generate notification
        notification = DocumentTemplates.generate_notification(
            notification_type=notification_type,
            **template_data
        )

        # Document metadata
        doc_date = datetime.now()

        content = {
            'type': notification_type,
            'subject': notification['subject'],
            'body': notification['body'],
            'date': doc_date,
            'customer': self.customer,
            'bank_name': self.bank_name,
            'sender': {
                'department': self._get_department(notification_type),
                'address': {
                    'street': self.data_generator.fake.street_address(),
                    'city': self.data_generator.fake.city(),
                    'state': self.data_generator.fake.state_abbr(),
                    'zip_code': self.data_generator.fake.zipcode(),
                }
            },
            'reference_number': self.data_generator.generate_reference_number(),
        }

        return content

    def _get_department(self, notification_type: str) -> str:
        """Get the sending department based on notification type."""
        departments = {
            'overdraft': 'Customer Service',
            'payment_received': 'Billing Department',
            'chargeback_notification': 'Risk Management',
            'statement_ready': 'Account Services',
            'kyc_reminder': 'Compliance Department',
            'suspicious_activity': 'Fraud Prevention',
            'address_change': 'Customer Service',
        }
        return departments.get(notification_type, 'Customer Service')

    def _generate_template_data(self, notification_type: str) -> Dict[str, str]:
        """
        Generate data to fill template variables.

        Args:
            notification_type: Type of notification

        Returns:
            dict: Template variable values
        """
        data = {
            'customer_name': self.customer['full_name'],
            'account_num': self.data_generator.generate_account_number()[-4:],
            'bank_name': self.bank_name,
            'phone': '1-800-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
        }

        # Add type-specific data
        if notification_type == 'overdraft':
            overdraft_amount = random.uniform(50, 500)
            balance = -overdraft_amount
            data.update({
                'balance': format_currency(balance),
                'overdraft_amount': format_currency(overdraft_amount),
            })

        elif notification_type == 'payment_received':
            amount = random.uniform(100, 2000)
            balance = random.uniform(500, 5000)
            data.update({
                'amount': format_currency(amount),
                'date': format_date(datetime.now()),
                'reference': self.data_generator.generate_reference_number(),
                'method': random.choice(['Online Payment', 'Check', 'Wire Transfer', 'ACH']),
                'balance': format_currency(balance),
            })

        elif notification_type == 'chargeback_notification':
            trans_date = datetime.now() - timedelta(days=random.randint(5, 30))
            amount = random.uniform(50, 500)
            reasons = [
                'Cardholder does not recognize transaction',
                'Product not received',
                'Duplicate charge',
                'Unauthorized transaction',
            ]
            data.update({
                'trans_date': format_date(trans_date),
                'amount': format_currency(amount),
                'reason': random.choice(reasons),
                'case_number': f'CB-{random.randint(100000, 999999)}',
            })

        elif notification_type == 'statement_ready':
            month = (datetime.now() - timedelta(days=30)).strftime('%B %Y')
            start = datetime.now() - timedelta(days=30)
            end = datetime.now()
            balance = random.uniform(1000, 10000)
            data.update({
                'month': month,
                'start_date': format_date(start),
                'end_date': format_date(end),
                'balance': format_currency(balance),
            })

        elif notification_type == 'suspicious_activity':
            merchant = self.data_generator.generate_merchant()
            amount = random.uniform(100, 1000)
            data.update({
                'account_last_four': self.data_generator.generate_account_number()[-4:],
                'date': format_date(datetime.now()),
                'merchant': merchant['name'],
                'amount': format_currency(amount),
                'location': merchant['full_location'],
            })

        elif notification_type == 'address_change':
            new_address = self.data_generator.generate_address()
            data.update({
                'new_address': f"{new_address['street']}\n{new_address['city']}, {new_address['state']} {new_address['zip_code']}",
            })

        return data

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics for size calculation.

        Args:
            content: Notification content

        Returns:
            dict: Metrics for size estimation
        """
        # Most notifications are 1-2 pages
        body_length = len(content['body'])

        num_pages = 1 if body_length < 2000 else 2
        num_paragraphs = content['body'].count('\n\n') + 3  # Paragraphs plus header/footer

        return {
            'num_pages': num_pages,
            'total_chars': body_length + 500,  # Body + header/footer
            'num_paragraphs': num_paragraphs,
        }
