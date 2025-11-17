"""
Bank statement generator.

Generates realistic bank account statements with transactions, balances,
and summary information.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from src.generators.base import StatementGenerator


class BankStatementGenerator(StatementGenerator):
    """
    Generates bank account statements.
    """

    def get_document_type(self) -> str:
        return 'bank_statement'

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate a bank statement with transactions and summary.

        Returns:
            dict: Complete bank statement data
        """
        # Statement period (usually one month)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Generate transactions
        num_transactions = self.config.get('num_transactions', random.randint(15, 40))
        opening_balance = self.config.get('opening_balance', random.uniform(500, 10000))

        transactions = self.data_generator.generate_bank_transactions(
            start_date=start_date,
            end_date=end_date,
            num_transactions=num_transactions,
            opening_balance=opening_balance
        )

        # Calculate summary
        closing_balance = transactions[-1]['balance'] if transactions else opening_balance

        total_deposits = sum(t['amount'] for t in transactions if t['amount'] > 0)
        total_withdrawals = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))

        # Count fees and interest
        fees = sum(abs(t['amount']) for t in transactions if t['amount'] < 0 and 'fee' in t['description'].lower())
        interest = sum(t['amount'] for t in transactions if t['amount'] > 0 and 'interest' in t['description'].lower())

        # Account type
        account_type = random.choice(['Checking', 'Savings', 'Money Market'])

        # Statement data
        content = {
            'bank_name': self.bank_name,
            'customer': self.customer,
            'account_number': self.account_number,
            'account_type': account_type,
            'routing_number': self.data_generator.generate_routing_number(),
            'statement_period': {
                'start': start_date,
                'end': end_date,
            },
            'opening_balance': round(opening_balance, 2),
            'closing_balance': round(closing_balance, 2),
            'summary': {
                'total_deposits': round(total_deposits, 2),
                'total_withdrawals': round(total_withdrawals, 2),
                'total_fees': round(fees, 2),
                'interest_earned': round(interest, 2),
                'number_of_deposits': sum(1 for t in transactions if t['amount'] > 0),
                'number_of_withdrawals': sum(1 for t in transactions if t['amount'] < 0),
            },
            'transactions': transactions,
            'contact_info': {
                'phone': '1-800-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
                'website': f'www.{self.bank_name.lower().replace(" ", "")}.com',
                'customer_service_hours': 'Monday-Friday 8am-8pm ET, Saturday 9am-5pm ET',
            }
        }

        return content

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics for size calculation.

        Args:
            content: Bank statement content

        Returns:
            dict: Metrics for size estimation
        """
        num_transactions = len(content['transactions'])

        # Estimate pages: ~30-40 transactions per page
        num_pages = max(1, (num_transactions // 35) + 1)

        # Estimate characters
        total_chars = 0
        # Header and customer info
        total_chars += 500
        # Summary section
        total_chars += 300
        # Each transaction (description + amount + date + balance)
        total_chars += num_transactions * 80

        return {
            'num_pages': num_pages,
            'total_chars': total_chars,
            'num_table_rows': num_transactions,
            'num_paragraphs': num_pages * 3,  # For DOCX
            'num_rows': num_transactions + 5,  # For XLSX (transactions + headers)
            'num_cols': 4,  # Date, Description, Amount, Balance
        }
