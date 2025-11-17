"""
Credit card statement generator.

Generates realistic credit card statements with purchases, payments,
interest charges, and summary information.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from src.generators.base import StatementGenerator


class CreditCardStatementGenerator(StatementGenerator):
    """
    Generates credit card statements.
    """

    def get_document_type(self) -> str:
        return 'credit_card_statement'

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate a credit card statement.

        Returns:
            dict: Complete credit card statement data
        """
        # Statement period (usually one month)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Card info
        card_type = random.choice(['visa', 'mastercard', 'amex', 'discover'])
        card_number = self.data_generator.generate_card_number(card_type)

        # Previous balance
        previous_balance = self.config.get('previous_balance', random.uniform(500, 3000))
        previous_balance = round(previous_balance, 2)

        # Generate purchases
        num_purchases = self.config.get('num_transactions', random.randint(10, 35))
        purchases = self.data_generator.generate_credit_card_transactions(
            start_date=start_date,
            end_date=end_date,
            num_transactions=num_purchases
        )

        total_purchases = sum(p['amount'] for p in purchases)

        # Generate payments (usually 1-3 payments per month)
        num_payments = random.randint(1, 3)
        payments = []
        total_payments = 0

        for _ in range(num_payments):
            payment_date = start_date + timedelta(days=random.randint(1, 28))
            # Payment typically covers 20-100% of previous balance
            payment_amount = random.uniform(previous_balance * 0.2, previous_balance)
            payment_amount = round(payment_amount, 2)
            total_payments += payment_amount

            payments.append({
                'date': payment_date,
                'description': 'Payment - Thank You',
                'amount': payment_amount
            })

        # Interest and fees
        apr = random.uniform(12.99, 24.99)
        daily_rate = apr / 365 / 100

        # Calculate average daily balance (simplified)
        average_balance = (previous_balance + total_purchases - total_payments) / 2
        days_in_period = (end_date - start_date).days
        interest_charged = round(average_balance * daily_rate * days_in_period, 2)

        # Fees
        fees = []
        total_fees = 0

        # Possibly add late fee
        if random.random() < 0.1:  # 10% chance
            late_fee = 35.00
            fees.append({'description': 'Late Payment Fee', 'amount': late_fee})
            total_fees += late_fee

        # Possibly add foreign transaction fees
        if random.random() < 0.3:  # 30% chance
            foreign_fee = round(random.uniform(5, 25), 2)
            fees.append({'description': 'Foreign Transaction Fee', 'amount': foreign_fee})
            total_fees += foreign_fee

        # Calculate new balance
        new_balance = previous_balance + total_purchases - total_payments + interest_charged + total_fees
        new_balance = round(new_balance, 2)

        # Minimum payment (usually 1-3% of balance, minimum $25)
        minimum_payment = max(25.00, round(new_balance * 0.02, 2))

        # Payment due date (usually 21-25 days after statement closing)
        due_date = end_date + timedelta(days=random.randint(21, 25))

        # Credit limit
        credit_limit = round(random.uniform(5000, 25000), -2)  # Round to nearest 100
        available_credit = credit_limit - new_balance

        # Rewards (if applicable)
        rewards_earned = 0
        if random.random() < 0.7:  # 70% of cards have rewards
            # Typically 1-2% cashback
            rewards_rate = random.choice([0.01, 0.015, 0.02])
            rewards_earned = round(total_purchases * rewards_rate, 2)

        content = {
            'bank_name': self.bank_name,
            'customer': self.customer,
            'account_number': self.account_number,
            'card_number': card_number,
            'card_type': card_type.upper(),
            'statement_period': {
                'start': start_date,
                'end': end_date,
            },
            'due_date': due_date,
            'summary': {
                'previous_balance': previous_balance,
                'total_purchases': round(total_purchases, 2),
                'total_payments': round(total_payments, 2),
                'interest_charged': interest_charged,
                'fees_charged': total_fees,
                'new_balance': new_balance,
                'minimum_payment': minimum_payment,
                'credit_limit': credit_limit,
                'available_credit': round(available_credit, 2),
                'apr': round(apr, 2),
                'rewards_earned': rewards_earned,
            },
            'purchases': sorted(purchases, key=lambda x: x['date']),
            'payments': sorted(payments, key=lambda x: x['date']),
            'fees': fees,
            'contact_info': {
                'phone': '1-800-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
                'website': f'www.{self.bank_name.lower().replace(" ", "")}.com',
                'customer_service_hours': '24/7',
            },
            'important_messages': [
                f"Your minimum payment of ${minimum_payment:.2f} is due by {due_date.strftime('%m/%d/%Y')}.",
                "To avoid additional interest charges, pay your balance in full.",
                "Late payments may result in fees and impact your credit score.",
            ]
        }

        return content

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics for size calculation.

        Args:
            content: Credit card statement content

        Returns:
            dict: Metrics for size estimation
        """
        num_purchases = len(content['purchases'])
        num_payments = len(content['payments'])
        total_transactions = num_purchases + num_payments + len(content['fees'])

        # Estimate pages
        num_pages = max(1, (total_transactions // 30) + 1)

        # Estimate characters
        total_chars = 0
        total_chars += 500  # Header
        total_chars += 400  # Summary
        total_chars += total_transactions * 70  # Transactions
        total_chars += 200  # Important messages

        return {
            'num_pages': num_pages,
            'total_chars': total_chars,
            'num_table_rows': total_transactions,
            'num_paragraphs': num_pages * 4,
            'num_rows': total_transactions + 8,  # For XLSX
            'num_cols': 4,
        }
