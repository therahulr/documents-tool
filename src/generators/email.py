"""
Email message generator.

Generates realistic email messages related to banking and payments,
suitable for MSG or EML format output.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.generators.base import EmailGenerator as BaseEmailGenerator
from src.data.templates import DocumentTemplates
from src.utils.formatting import format_currency, format_date


class EmailGenerator(BaseEmailGenerator):
    """
    Generates email messages for banking/payment notifications.
    """

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate an email message.

        Returns:
            dict: Complete email data
        """
        # Generate sender and recipient
        sender_bank = self.data_generator.generate_bank_name()
        sender_dept = random.choice([
            'Customer Service',
            'Account Services',
            'Billing Department',
            'Security Team',
            'Notifications',
        ])

        sender_email = f'{sender_dept.lower().replace(" ", ".")}@{sender_bank.lower().replace(" ", "")}.com'

        # Recipient (customer)
        recipient_person = self.data_generator.generate_person()

        # Email type
        email_type = self.config.get('email_type', random.choice([
            'statement',
            'payment',
            'alert',
            'notification'
        ]))

        # Generate subject and body based on type
        if email_type == 'statement':
            content = self._generate_statement_email(sender_bank, recipient_person)
        elif email_type == 'payment':
            content = self._generate_payment_email(sender_bank, recipient_person)
        elif email_type == 'alert':
            content = self._generate_alert_email(sender_bank, recipient_person)
        else:
            content = self._generate_notification_email(sender_bank, recipient_person)

        # Build complete email
        email_data = {
            'from': {
                'name': f'{sender_bank} {sender_dept}',
                'email': sender_email,
            },
            'to': {
                'name': recipient_person['full_name'],
                'email': recipient_person['email'],
            },
            'cc': [],
            'bcc': [],
            'subject': content['subject'],
            'date': datetime.now(),
            'body_text': content['body_text'],
            'body_html': content['body_html'],
            'attachments': content.get('attachments', []),
            'priority': content.get('priority', 'normal'),
        }

        return email_data

    def _generate_statement_email(self, bank_name: str, recipient: Dict[str, str]) -> Dict[str, Any]:
        """Generate a statement notification email."""
        month = (datetime.now() - timedelta(days=5)).strftime('%B %Y')

        subject = DocumentTemplates.get_email_subject('statement', month=month, bank_name=bank_name, year=datetime.now().year)

        body_text = f"""
Dear {recipient['full_name']},

Your monthly statement for {month} is now available for viewing.

You can access your statement by:
- Logging in to your account at www.{bank_name.lower().replace(' ', '')}.com
- Using our mobile app
- Calling our customer service at 1-800-{random.randint(1000000, 9999999)}

To help protect the environment and reduce paper waste, consider enrolling in paperless statements.

If you have any questions about your statement, please don't hesitate to contact us.

Thank you for being a valued customer.

Best regards,
{bank_name} Account Services

---
This is an automated message. Please do not reply to this email.
"""

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0066cc;">Your Statement is Ready</h2>

        <p>Dear {recipient['full_name']},</p>

        <p>Your monthly statement for <strong>{month}</strong> is now available for viewing.</p>

        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Access Your Statement:</h3>
            <ul>
                <li>Log in to your account at <a href="http://www.{bank_name.lower().replace(' ', '')}.com">our website</a></li>
                <li>Use our mobile app</li>
                <li>Call customer service at 1-800-{random.randint(1000000, 9999999)}</li>
            </ul>
        </div>

        <p>To help protect the environment and reduce paper waste, consider enrolling in paperless statements.</p>

        <p>If you have any questions about your statement, please don't hesitate to contact us.</p>

        <p>Thank you for being a valued customer.</p>

        <p style="margin-top: 30px;">
            Best regards,<br>
            <strong>{bank_name} Account Services</strong>
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="font-size: 12px; color: #666;">
            This is an automated message. Please do not reply to this email.
        </p>
    </div>
</body>
</html>
"""

        return {
            'subject': subject,
            'body_text': body_text.strip(),
            'body_html': body_html,
        }

    def _generate_payment_email(self, bank_name: str, recipient: Dict[str, str]) -> Dict[str, Any]:
        """Generate a payment confirmation email."""
        amount = format_currency(random.uniform(100, 2000))
        ref_num = self.data_generator.generate_reference_number()

        subject = DocumentTemplates.get_email_subject('payment', amount=amount)

        body_text = f"""
Dear {recipient['full_name']},

This email confirms that we have received your payment.

Payment Details:
- Amount: {amount}
- Date: {format_date(datetime.now())}
- Reference Number: {ref_num}
- Payment Method: Online Payment

Your payment has been successfully processed and will be reflected in your account within 1-2 business days.

If you did not authorize this payment, please contact us immediately at 1-800-{random.randint(1000000, 9999999)}.

Thank you for your prompt payment.

Sincerely,
{bank_name} Billing Department
"""

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #4CAF50; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">✓ Payment Received</h2>
        </div>

        <p>Dear {recipient['full_name']},</p>

        <p>This email confirms that we have received your payment.</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f5f5f5;">
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Detail</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Value</th>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Amount</td>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>{amount}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Date</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{format_date(datetime.now())}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Reference Number</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ref_num}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Payment Method</td>
                <td style="padding: 10px; border: 1px solid #ddd;">Online Payment</td>
            </tr>
        </table>

        <p>Your payment has been successfully processed and will be reflected in your account within 1-2 business days.</p>

        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <strong>Security Note:</strong> If you did not authorize this payment, please contact us immediately at 1-800-{random.randint(1000000, 9999999)}.
        </div>

        <p>Thank you for your prompt payment.</p>

        <p style="margin-top: 30px;">
            Sincerely,<br>
            <strong>{bank_name} Billing Department</strong>
        </p>
    </div>
</body>
</html>
"""

        return {
            'subject': subject,
            'body_text': body_text.strip(),
            'body_html': body_html,
        }

    def _generate_alert_email(self, bank_name: str, recipient: Dict[str, str]) -> Dict[str, Any]:
        """Generate a security alert email."""
        merchant = self.data_generator.generate_merchant()
        amount = format_currency(random.uniform(50, 800))

        subject = "Security Alert: Unusual Activity on Your Account"

        body_text = f"""
Dear {recipient['full_name']},

We detected unusual activity on your account and wanted to verify it with you.

Transaction Details:
- Merchant: {merchant['name']}
- Location: {merchant['full_location']}
- Amount: {amount}
- Date: {format_date(datetime.now())}

If you recognize this transaction:
No action is needed. Your account remains secure.

If you DO NOT recognize this transaction:
Please call us immediately at 1-800-{random.randint(1000000, 9999999)} or log in to your account to report it.

For your security, we have temporarily restricted your account until we hear from you.

Your security is our top priority.

Sincerely,
{bank_name} Security Team
"""

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ff9800; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">⚠ Security Alert</h2>
        </div>

        <p>Dear {recipient['full_name']},</p>

        <p>We detected unusual activity on your account and wanted to verify it with you.</p>

        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Transaction Details:</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Merchant:</strong> {merchant['name']}</li>
                <li><strong>Location:</strong> {merchant['full_location']}</li>
                <li><strong>Amount:</strong> {amount}</li>
                <li><strong>Date:</strong> {format_date(datetime.now())}</li>
            </ul>
        </div>

        <div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #4CAF50;">If you recognize this transaction:</h3>
            <p>No action is needed. Your account remains secure.</p>
        </div>

        <div style="border: 2px solid #f44336; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #f44336;">If you DO NOT recognize this transaction:</h3>
            <p>Please call us immediately at <strong>1-800-{random.randint(1000000, 9999999)}</strong> or log in to your account to report it.</p>
        </div>

        <p style="background-color: #fff3cd; padding: 15px; border-radius: 5px;">
            For your security, we have temporarily restricted your account until we hear from you.
        </p>

        <p>Your security is our top priority.</p>

        <p style="margin-top: 30px;">
            Sincerely,<br>
            <strong>{bank_name} Security Team</strong>
        </p>
    </div>
</body>
</html>
"""

        return {
            'subject': subject,
            'body_text': body_text.strip(),
            'body_html': body_html,
            'priority': 'high',
        }

    def _generate_notification_email(self, bank_name: str, recipient: Dict[str, str]) -> Dict[str, Any]:
        """Generate a general notification email."""
        notification_types = ['kyc_reminder', 'address_change', 'statement_ready']
        notif_type = random.choice(notification_types)

        # Generate notification content
        template_data = {
            'customer_name': recipient['full_name'],
            'bank_name': bank_name,
            'phone': '1-800-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
            'account_num': self.data_generator.generate_account_number()[-4:],
        }

        if notif_type == 'statement_ready':
            month = (datetime.now() - timedelta(days=30)).strftime('%B %Y')
            template_data.update({
                'month': month,
                'start_date': format_date(datetime.now() - timedelta(days=30)),
                'end_date': format_date(datetime.now()),
                'balance': format_currency(random.uniform(1000, 10000)),
            })
        elif notif_type == 'address_change':
            new_address = self.data_generator.generate_address()
            template_data['new_address'] = f"{new_address['street']}\n{new_address['city']}, {new_address['state']} {new_address['zip_code']}"

        notification = DocumentTemplates.generate_notification(notif_type, **template_data)

        # Convert to HTML
        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0066cc;">{bank_name}</h2>
        {''.join(f'<p>{para}</p>' for para in notification['body'].split('\n\n'))}
    </div>
</body>
</html>
"""

        return {
            'subject': notification['subject'],
            'body_text': notification['body'],
            'body_html': body_html,
        }

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics for size calculation.

        Args:
            content: Email content

        Returns:
            dict: Metrics for size estimation
        """
        body_chars = len(content.get('body_html', ''))
        num_headers = 5  # From, To, Subject, Date, etc.

        attachment_size_kb = 0
        if content.get('attachments'):
            # If attachments are specified, estimate their size
            for att in content['attachments']:
                attachment_size_kb += att.get('size_kb', 0)

        return {
            'body_chars': body_chars,
            'num_headers': num_headers,
            'attachment_size_kb': attachment_size_kb,
        }
