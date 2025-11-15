"""
Document content templates for various document types.

Contains realistic, domain-specific text content for financial documents.
NO LOREM IPSUM - all content is meaningful and realistic.
"""

import random
from typing import List


class DocumentTemplates:
    """
    Provides realistic content templates for various document types.
    """

    # ========== Terms & Conditions Sections ==========

    TC_SECTIONS = {
        'introduction': [
            """
            These Terms and Conditions ("Agreement") govern your use of payment processing
            services provided by {bank_name} ("we," "us," or "our"). By accessing or using
            our services, you agree to be bound by these terms. Please read them carefully.
            """,
            """
            This Agreement establishes the terms under which {bank_name} will provide
            payment processing and financial services to you ("Customer," "you," or "your").
            Your continued use of our services constitutes acceptance of these terms.
            """,
        ],

        'definitions': [
            """
            "Account" means your payment processing account established with {bank_name}.
            "Transaction" means any payment, transfer, or financial operation processed through our services.
            "Business Day" means Monday through Friday, excluding federal holidays.
            "Chargeback" means a transaction reversal initiated by a cardholder's issuing bank.
            "Settlement" means the process of transferring funds to your designated account.
            """,
        ],

        'account_terms': [
            """
            You must provide accurate and complete information when opening an account.
            You are responsible for maintaining the confidentiality of your account credentials.
            You must notify us immediately of any unauthorized access to your account.
            We reserve the right to suspend or terminate accounts that violate these terms.
            Account ownership cannot be transferred without our prior written consent.
            """,
        ],

        'payment_processing': [
            """
            We will process transactions submitted through approved channels in accordance
            with applicable payment network rules. Processing times vary by transaction type
            and may take 1-3 business days. We reserve the right to reject transactions that
            appear fraudulent or violate our acceptable use policy. Transaction limits may
            apply based on your account type and history.
            """,
            """
            All transactions are subject to verification and fraud screening. We employ
            industry-standard security measures to protect transaction data. You acknowledge
            that processing times are estimates and may vary based on factors outside our
            control, including payment network delays and banking holidays.
            """,
        ],

        'fees': [
            """
            Fees for our services are detailed in your Fee Schedule, incorporated herein by
            reference. Standard fees include transaction fees, monthly account fees, and
            chargeback fees. We reserve the right to modify fees with 30 days' notice.
            Additional fees may apply for specialized services, rush processing, or
            international transactions. All fees are non-refundable unless otherwise stated.
            """,
            """
            You agree to pay all applicable fees as set forth in the Fee Schedule. Fees will
            be automatically deducted from your settlement funds. If settlement funds are
            insufficient, you authorize us to debit your designated bank account. Failure to
            pay fees may result in account suspension or termination. Volume discounts may be
            available for qualifying businesses.
            """,
        ],

        'chargebacks': [
            """
            You are responsible for all chargebacks and associated fees. When a chargeback
            occurs, the transaction amount plus applicable fees will be deducted from your
            account. You have the right to dispute chargebacks by providing supporting
            documentation within the timeframe specified by the card networks. We will assist
            in the dispute process but cannot guarantee favorable outcomes. Excessive
            chargebacks may result in account termination or reserve requirements.
            """,
        ],

        'settlement': [
            """
            Funds will be settled to your designated bank account according to your settlement
            schedule, typically within 1-3 business days. We may establish reserves or holdbacks
            based on your business type, transaction volume, or risk profile. Settlement may be
            delayed if we suspect fraudulent activity or if additional verification is required.
            You are responsible for ensuring your bank account information is accurate and current.
            """,
        ],

        'disputes': [
            """
            Any disputes arising from this Agreement shall be resolved through binding arbitration
            in accordance with the rules of the American Arbitration Association. You waive any
            right to participate in class action lawsuits. This Agreement is governed by the laws
            of the state in which our principal office is located, without regard to conflict of
            law principles. Legal proceedings must be initiated within one year of the dispute arising.
            """,
        ],

        'data_privacy': [
            """
            We collect and process personal and financial data in accordance with our Privacy Policy
            and applicable data protection laws. We implement appropriate technical and organizational
            measures to protect your data. We do not sell your personal information to third parties.
            Data may be shared with payment processors, financial institutions, and service providers
            necessary to deliver our services. You have rights to access, correct, and delete your
            personal data subject to legal and regulatory requirements.
            """,
        ],

        'termination': [
            """
            Either party may terminate this Agreement with 30 days' written notice. We may
            immediately suspend or terminate your account if you violate these terms, engage in
            fraudulent activity, or if we are required to do so by law or payment network rules.
            Upon termination, you remain liable for all outstanding fees, chargebacks, and obligations.
            We will settle any remaining funds after deducting applicable fees and reserves.
            """,
        ],

        'liability': [
            """
            Our liability is limited to direct damages not exceeding the fees paid by you in the
            12 months preceding the claim. We are not liable for indirect, incidental, consequential,
            or punitive damages. We do not guarantee uninterrupted service and are not liable for
            losses due to service outages, technical issues, or third-party failures. You agree to
            indemnify us against claims arising from your use of our services or violation of these terms.
            """,
        ],

        'modifications': [
            """
            We reserve the right to modify these Terms and Conditions at any time. Material changes
            will be communicated via email or through your account dashboard at least 30 days before
            the effective date. Your continued use of our services after changes take effect constitutes
            acceptance of the modified terms. If you do not agree to the changes, you may terminate
            your account without penalty before the effective date.
            """,
        ],
    }

    @classmethod
    def generate_terms_and_conditions(cls, bank_name: str, num_sections: int = None) -> List[Dict[str, str]]:
        """
        Generate a complete Terms & Conditions document.

        Args:
            bank_name: Name of the financial institution
            num_sections: Number of sections to include (random if None)

        Returns:
            list: List of sections with titles and content
        """
        if num_sections is None:
            num_sections = random.randint(6, len(cls.TC_SECTIONS))

        # Always include introduction
        sections = [
            {
                'title': '1. Introduction and Acceptance',
                'content': random.choice(cls.TC_SECTIONS['introduction']).format(bank_name=bank_name).strip()
            }
        ]

        # Select other sections
        available_sections = [k for k in cls.TC_SECTIONS.keys() if k != 'introduction']
        selected = random.sample(available_sections, min(num_sections - 1, len(available_sections)))

        section_titles = {
            'definitions': 'Definitions',
            'account_terms': 'Account Terms and Responsibilities',
            'payment_processing': 'Payment Processing',
            'fees': 'Fees and Charges',
            'chargebacks': 'Chargebacks and Disputes',
            'settlement': 'Settlement and Reserves',
            'disputes': 'Dispute Resolution and Governing Law',
            'data_privacy': 'Data Privacy and Security',
            'termination': 'Termination',
            'liability': 'Limitation of Liability',
            'modifications': 'Modifications to Terms',
        }

        for i, key in enumerate(selected, start=2):
            content = random.choice(cls.TC_SECTIONS[key])
            if '{bank_name}' in content:
                content = content.format(bank_name=bank_name)

            sections.append({
                'title': f'{i}. {section_titles[key]}',
                'content': content.strip()
            })

        return sections

    # ========== Notification Templates ==========

    NOTIFICATION_TYPES = {
        'overdraft': {
            'subject': 'Important: Overdraft Notice for Account {account_num}',
            'body': """
Dear {customer_name},

We are writing to inform you that your account {account_num} has been overdrawn.

Current balance: {balance}
Overdraft amount: {overdraft_amount}
Overdraft fee: $35.00

To avoid additional fees, please deposit funds to bring your account to a positive balance
as soon as possible. You can make a deposit at any branch, through our mobile app, or via
direct deposit.

If you have questions about overdraft protection or would like to discuss your account,
please contact us at {phone} or visit your nearest branch.

Thank you for banking with {bank_name}.

Sincerely,
{bank_name} Customer Service
            """
        },

        'payment_received': {
            'subject': 'Payment Received - Confirmation',
            'body': """
Dear {customer_name},

We have successfully received your payment.

Payment Details:
- Amount: {amount}
- Payment Date: {date}
- Reference Number: {reference}
- Payment Method: {method}

Your new account balance is {balance}. This payment will be reflected in your account
within 1-2 business days.

Thank you for your prompt payment. If you have any questions, please contact us at {phone}.

Best regards,
{bank_name} Billing Department
            """
        },

        'chargeback_notification': {
            'subject': 'Chargeback Notification - Action Required',
            'body': """
Dear {customer_name},

We have received a chargeback for a transaction processed through your account.

Chargeback Details:
- Transaction Date: {trans_date}
- Transaction Amount: {amount}
- Reason: {reason}
- Case Number: {case_number}

The disputed amount plus a $25.00 chargeback fee has been deducted from your account.

If you wish to dispute this chargeback, please submit supporting documentation (receipt,
proof of delivery, customer communication) through your account dashboard within 7 days.

For assistance, please contact our Merchant Support team at {phone}.

Sincerely,
{bank_name} Risk Management
            """
        },

        'statement_ready': {
            'subject': 'Your {month} Statement is Ready',
            'body': """
Dear {customer_name},

Your monthly statement for {month} is now available.

Statement Period: {start_date} - {end_date}
Ending Balance: {balance}

You can view and download your statement by logging into your account at our website
or mobile app. Paper statements can be requested for a $2.00 fee.

If you have questions about your statement, please contact us at {phone}.

Thank you for being a valued customer.

Best regards,
{bank_name}
            """
        },

        'kyc_reminder': {
            'subject': 'Action Required: Update Your Account Information',
            'body': """
Dear {customer_name},

As part of our ongoing commitment to security and regulatory compliance, we need you to
update your account information.

Required Actions:
- Verify your current address
- Confirm your phone number and email
- Review your account settings

Please log in to your account and complete the verification process within 30 days. Failure
to complete this process may result in temporary restrictions on your account.

This is a routine procedure required by banking regulations to prevent fraud and ensure the
security of your account.

If you need assistance, please contact us at {phone}.

Thank you for your cooperation.

Sincerely,
{bank_name} Compliance Department
            """
        },

        'suspicious_activity': {
            'subject': 'Security Alert: Unusual Activity Detected',
            'body': """
Dear {customer_name},

We have detected unusual activity on your account ending in {account_last_four}.

Flagged Transaction:
- Date: {date}
- Merchant: {merchant}
- Amount: {amount}
- Location: {location}

If you recognize this transaction, no action is needed. If you did not authorize this
transaction, please contact us immediately at {phone}.

For your security, we have temporarily placed a hold on your account. You can remove this
hold by verifying the transaction through our mobile app or by calling us.

Your security is our priority. We apologize for any inconvenience.

Best regards,
{bank_name} Fraud Prevention Team
            """
        },

        'address_change': {
            'subject': 'Address Change Confirmation',
            'body': """
Dear {customer_name},

This confirms that we have updated the mailing address for your account {account_num}.

New Address:
{new_address}

This change is effective immediately. Future statements and correspondence will be sent to
this address.

If you did not request this change, please contact us immediately at {phone}.

Thank you for keeping your account information current.

Sincerely,
{bank_name} Customer Service
            """
        },
    }

    @classmethod
    def generate_notification(cls, notification_type: str, **kwargs) -> Dict[str, str]:
        """
        Generate a notification letter or email.

        Args:
            notification_type: Type of notification
            **kwargs: Variables to fill in the template

        Returns:
            dict: Notification with subject and body
        """
        if notification_type not in cls.NOTIFICATION_TYPES:
            notification_type = random.choice(list(cls.NOTIFICATION_TYPES.keys()))

        template = cls.NOTIFICATION_TYPES[notification_type]

        # Fill in template variables
        subject = template['subject'].format(**kwargs)
        body = template['body'].format(**kwargs).strip()

        return {
            'type': notification_type,
            'subject': subject,
            'body': body
        }

    # ========== Email Subject Lines ==========

    EMAIL_SUBJECTS = {
        'statement': [
            "Your {month} {year} Statement is Available",
            "Monthly Account Statement - {month} {year}",
            "{bank_name} Statement for {month}",
        ],
        'payment': [
            "Payment Confirmation - {amount}",
            "Payment Received Successfully",
            "Your Payment of {amount} Has Been Processed",
        ],
        'alert': [
            "Important Account Alert",
            "Security Notification for Your Account",
            "Action Required: Account Verification",
        ],
        'marketing': [
            "Exclusive Offer for Valued Customers",
            "New Features Available on Your Account",
            "Upgrade Your Account Today",
        ],
    }

    @classmethod
    def get_email_subject(cls, subject_type: str = 'statement', **kwargs) -> str:
        """
        Get an email subject line.

        Args:
            subject_type: Type of email
            **kwargs: Variables to format the subject

        Returns:
            str: Email subject line
        """
        if subject_type not in cls.EMAIL_SUBJECTS:
            subject_type = 'statement'

        template = random.choice(cls.EMAIL_SUBJECTS[subject_type])
        return template.format(**kwargs)
