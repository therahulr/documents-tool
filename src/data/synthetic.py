"""
Synthetic data generator for payment and banking domain.

This module generates realistic synthetic data using Faker and custom logic.
All data is clearly synthetic and suitable for testing purposes only.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from faker import Faker


class SyntheticDataGenerator:
    """
    Generates realistic synthetic data for payment and banking documents.
    """

    def __init__(self, seed: int = None, locale: str = 'en_US'):
        """
        Initialize the synthetic data generator.

        Args:
            seed: Random seed for reproducibility (optional)
            locale: Locale for Faker (default: en_US for American data)
        """
        self.fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    # ========== Personal Information ==========

    def generate_person(self) -> Dict[str, str]:
        """Generate a synthetic person with full details."""
        return {
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'full_name': self.fake.name(),
            'email': self.fake.email(),
            'phone': self.fake.phone_number(),
            'ssn': self.fake.ssn(),  # Clearly synthetic
        }

    def generate_address(self) -> Dict[str, str]:
        """Generate a synthetic US address."""
        return {
            'street': self.fake.street_address(),
            'city': self.fake.city(),
            'state': self.fake.state_abbr(),
            'state_full': self.fake.state(),
            'zip_code': self.fake.zipcode(),
            'country': 'USA',
        }

    # ========== Financial Institutions ==========

    SYNTHETIC_BANKS = [
        "Pacific Trust Bank",
        "Chenshire Financial Group",
        "Metropolitan Savings & Loan",
        "Riverside Community Bank",
        "Summit National Bank",
        "Heritage Federal Credit Union",
        "Pioneer Bank & Trust",
        "Gateway Financial Services",
        "Cornerstone Bank",
        "Liberty National Bank",
        "Commonwealth Credit Union",
        "Northstar Financial",
        "Cascade Banking Corporation",
        "Pinnacle Trust Company",
        "Unity Federal Bank",
    ]

    def generate_bank_name(self) -> str:
        """Generate a synthetic bank name."""
        return random.choice(self.SYNTHETIC_BANKS)

    def generate_account_number(self, length: int = 10) -> str:
        """
        Generate a realistic account number (not trivial sequence).

        Args:
            length: Length of account number

        Returns:
            str: Account number
        """
        # Avoid trivial sequences like 0000, 1111, 12345
        # Use random digits that look realistic
        parts = []
        for _ in range(length):
            parts.append(str(random.randint(0, 9)))

        # Ensure it's not all same digits
        account = ''.join(parts)
        if len(set(account)) == 1:  # All same digit
            # Replace one digit
            pos = random.randint(0, len(account) - 1)
            account = account[:pos] + str((int(account[pos]) + 1) % 10) + account[pos+1:]

        return account

    def generate_routing_number(self) -> str:
        """Generate a synthetic routing number (9 digits)."""
        # Real routing numbers have a checksum, but for testing we'll use random
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])

    def generate_card_number(self, card_type: str = 'visa') -> str:
        """
        Generate a synthetic credit card number.

        Args:
            card_type: Type of card ('visa', 'mastercard', 'amex', 'discover')

        Returns:
            str: 16-digit card number (15 for Amex)
        """
        if card_type == 'visa':
            prefix = '4'
            length = 16
        elif card_type == 'mastercard':
            prefix = '5' + str(random.randint(1, 5))
            length = 16
        elif card_type == 'amex':
            prefix = '3' + random.choice(['4', '7'])
            length = 15
        elif card_type == 'discover':
            prefix = '6011'
            length = 16
        else:
            prefix = '4'  # Default to Visa
            length = 16

        # Generate remaining digits
        remaining = length - len(prefix)
        number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(remaining)])

        return number

    # ========== Merchants & Transactions ==========

    MERCHANT_CATEGORIES = {
        'groceries': [
            "Whole Foods Market", "Trader Joe's", "Safeway", "Kroger",
            "Publix", "Walmart Supercenter", "Target", "Costco Wholesale",
            "Aldi", "Food Lion"
        ],
        'restaurants': [
            "The Olive Garden", "Chipotle Mexican Grill", "Panera Bread",
            "Cheesecake Factory", "Red Lobster", "Applebee's",
            "Buffalo Wild Wings", "Starbucks", "Dunkin'", "McDonald's",
            "Subway", "Chick-fil-A", "Five Guys"
        ],
        'gas_stations': [
            "Shell", "Chevron", "BP", "Exxon", "Mobil", "Texaco",
            "Sunoco", "Arco", "Circle K", "7-Eleven"
        ],
        'utilities': [
            "Pacific Gas & Electric", "Commonwealth Edison",
            "Duke Energy", "AT&T", "Verizon Wireless", "Comcast",
            "Spectrum", "Water District", "City of {} Utilities"
        ],
        'online': [
            "Amazon.com", "eBay", "Etsy", "Wayfair", "Best Buy Online",
            "Apple.com", "Netflix", "Spotify", "Adobe Creative Cloud",
            "Microsoft 365", "Google Workspace", "Dropbox"
        ],
        'retail': [
            "Target", "Walmart", "Best Buy", "Home Depot", "Lowe's",
            "Macy's", "Nordstrom", "Kohl's", "TJ Maxx", "Ross",
            "CVS Pharmacy", "Walgreens", "Rite Aid"
        ],
        'entertainment': [
            "AMC Theatres", "Regal Cinemas", "Live Nation",
            "Ticketmaster", "Steam Games", "PlayStation Store",
            "Xbox Store", "Nintendo eShop", "Spotify Premium"
        ],
        'healthcare': [
            "CVS Pharmacy", "Walgreens", "{} Medical Center",
            "{} Dental", "Vision Care Associates", "HealthFirst Clinic"
        ],
        'transportation': [
            "Uber", "Lyft", "United Airlines", "Delta Air Lines",
            "Southwest Airlines", "Hertz Rent-A-Car", "Enterprise",
            "Amtrak", "Metro Transit"
        ],
        'insurance': [
            "State Farm Insurance", "Allstate", "GEICO",
            "Progressive", "Nationwide", "Farmers Insurance"
        ]
    }

    def generate_merchant(self, category: str = None) -> Dict[str, str]:
        """
        Generate a synthetic merchant.

        Args:
            category: Merchant category (optional, random if not specified)

        Returns:
            dict: Merchant information with name, city, state, category
        """
        if category is None or category not in self.MERCHANT_CATEGORIES:
            category = random.choice(list(self.MERCHANT_CATEGORIES.keys()))

        merchant_name = random.choice(self.MERCHANT_CATEGORIES[category])

        # Some merchant names have placeholders for city
        if '{}' in merchant_name:
            merchant_name = merchant_name.format(self.fake.city())

        city = self.fake.city()
        state = self.fake.state_abbr()

        return {
            'name': merchant_name,
            'city': city,
            'state': state,
            'category': category,
            'full_location': f"{city}, {state}"
        }

    def generate_transaction_amount(self, category: str = None) -> float:
        """
        Generate a realistic transaction amount based on category.

        Args:
            category: Transaction category

        Returns:
            float: Transaction amount
        """
        amount_ranges = {
            'groceries': (20.0, 250.0),
            'restaurants': (8.0, 120.0),
            'gas_stations': (25.0, 85.0),
            'utilities': (50.0, 350.0),
            'online': (10.0, 500.0),
            'retail': (15.0, 400.0),
            'entertainment': (10.0, 150.0),
            'healthcare': (30.0, 500.0),
            'transportation': (8.0, 800.0),
            'insurance': (100.0, 500.0),
        }

        if category in amount_ranges:
            min_amt, max_amt = amount_ranges[category]
        else:
            min_amt, max_amt = (10.0, 200.0)

        amount = random.uniform(min_amt, max_amt)
        return round(amount, 2)

    # ========== Bank Transactions ==========

    def generate_bank_transaction(
        self,
        date: datetime,
        transaction_type: str = None,
        balance: float = None
    ) -> Dict[str, Any]:
        """
        Generate a bank transaction.

        Args:
            date: Transaction date
            transaction_type: 'debit', 'credit', or None (random)
            balance: Current balance for balance calculation

        Returns:
            dict: Transaction details
        """
        if transaction_type is None:
            transaction_type = random.choice(['debit', 'debit', 'debit', 'credit'])

        if transaction_type == 'debit':
            # Debits: purchases, withdrawals, fees
            sub_type = random.choice(['purchase', 'purchase', 'purchase', 'atm', 'fee', 'transfer'])

            if sub_type == 'purchase':
                merchant = self.generate_merchant()
                description = f"{merchant['name']} {merchant['full_location']}"
                amount = self.generate_transaction_amount(merchant['category'])
            elif sub_type == 'atm':
                description = f"ATM Withdrawal - {self.fake.street_name()} Branch"
                amount = random.choice([20, 40, 60, 80, 100, 120, 140, 160, 200])
            elif sub_type == 'fee':
                fee_types = [
                    ("Monthly Service Fee", 12.00),
                    ("Overdraft Fee", 35.00),
                    ("ATM Fee - Out of Network", 3.00),
                    ("Wire Transfer Fee", 25.00),
                    ("Foreign Transaction Fee", random.uniform(2, 15)),
                ]
                description, amount = random.choice(fee_types)
                amount = round(amount, 2)
            else:  # transfer
                description = f"Transfer to {self.generate_account_number(4)}****"
                amount = random.uniform(50, 2000)
                amount = round(amount, 2)

            amount = -abs(amount)  # Debits are negative

        else:  # credit
            sub_type = random.choice(['deposit', 'deposit', 'transfer', 'interest', 'refund'])

            if sub_type == 'deposit':
                deposit_types = [
                    "Direct Deposit - Payroll",
                    "Mobile Check Deposit",
                    "ATM Deposit",
                    "Wire Transfer Received",
                ]
                description = random.choice(deposit_types)
                if "Payroll" in description:
                    amount = random.uniform(1500, 5000)
                else:
                    amount = random.uniform(100, 3000)
            elif sub_type == 'transfer':
                description = f"Transfer from {self.generate_account_number(4)}****"
                amount = random.uniform(50, 2000)
            elif sub_type == 'interest':
                description = "Interest Earned"
                amount = random.uniform(0.05, 25.0)
            else:  # refund
                merchant = self.generate_merchant()
                description = f"Refund - {merchant['name']}"
                amount = random.uniform(10, 200)

            amount = abs(amount)
            amount = round(amount, 2)

        return {
            'date': date,
            'description': description,
            'amount': amount,
            'type': transaction_type,
            'balance': balance,  # Will be calculated by caller
        }

    def generate_bank_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        num_transactions: int = None,
        opening_balance: float = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a realistic series of bank transactions.

        Args:
            start_date: Start date for transactions
            end_date: End date for transactions
            num_transactions: Number of transactions (random if None)
            opening_balance: Starting balance (random if None)

        Returns:
            list: List of transactions with running balance
        """
        if num_transactions is None:
            days = (end_date - start_date).days
            num_transactions = random.randint(max(10, days // 2), max(20, days))

        if opening_balance is None:
            opening_balance = random.uniform(500, 10000)
            opening_balance = round(opening_balance, 2)

        transactions = []
        current_balance = opening_balance

        # Generate random dates within the range
        dates = []
        for _ in range(num_transactions):
            random_date = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            dates.append(random_date)

        dates.sort()

        # Generate transactions
        for date in dates:
            transaction = self.generate_bank_transaction(date, balance=current_balance)
            current_balance += transaction['amount']
            current_balance = round(current_balance, 2)
            transaction['balance'] = current_balance
            transactions.append(transaction)

        return transactions

    # ========== Credit Card Transactions ==========

    def generate_credit_card_transaction(self, date: datetime) -> Dict[str, Any]:
        """
        Generate a credit card transaction.

        Args:
            date: Transaction date

        Returns:
            dict: Transaction details
        """
        merchant = self.generate_merchant()
        amount = self.generate_transaction_amount(merchant['category'])

        return {
            'date': date,
            'merchant': merchant['name'],
            'location': merchant['full_location'],
            'category': merchant['category'],
            'amount': amount,
        }

    def generate_credit_card_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        num_transactions: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate credit card transactions for a statement period.

        Args:
            start_date: Statement start date
            end_date: Statement end date
            num_transactions: Number of transactions (random if None)

        Returns:
            list: List of credit card transactions
        """
        if num_transactions is None:
            days = (end_date - start_date).days
            num_transactions = random.randint(max(5, days // 3), max(15, days))

        transactions = []
        dates = []
        for _ in range(num_transactions):
            random_date = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            dates.append(random_date)

        dates.sort()

        for date in dates:
            transactions.append(self.generate_credit_card_transaction(date))

        return transactions

    # ========== Invoice & Payment Data ==========

    def generate_invoice_number(self) -> str:
        """Generate an invoice number."""
        prefix = random.choice(['INV', 'BILL', 'PAY'])
        year = datetime.now().year
        number = random.randint(10000, 99999)
        return f"{prefix}-{year}-{number}"

    def generate_reference_number(self) -> str:
        """Generate a payment reference number."""
        return ''.join([str(random.randint(0, 9)) for _ in range(12)])

    def generate_line_items(self, num_items: int = None) -> List[Dict[str, Any]]:
        """
        Generate invoice line items.

        Args:
            num_items: Number of line items (random if None)

        Returns:
            list: List of line items
        """
        if num_items is None:
            num_items = random.randint(1, 8)

        items = []
        item_names = [
            "Professional Services", "Consulting Fee", "Software License",
            "Maintenance Fee", "Support Services", "Training Session",
            "Product Purchase", "Shipping & Handling", "Processing Fee",
            "Administrative Fee", "Setup Fee", "Monthly Subscription"
        ]

        for _ in range(num_items):
            quantity = random.randint(1, 10)
            unit_price = random.uniform(10, 500)
            unit_price = round(unit_price, 2)
            total = quantity * unit_price

            items.append({
                'description': random.choice(item_names),
                'quantity': quantity,
                'unit_price': unit_price,
                'total': round(total, 2)
            })

        return items
