"""
Seed data loader.

Loads real-world datasets from CSV files to generate realistic synthetic documents.
"""

import csv
import random
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class SeedDataLoader:
    """
    Loads and provides access to seed datasets.
    """

    def __init__(self, seed_data_path: str = None):
        """
        Initialize the seed data loader.

        Args:
            seed_data_path: Path to seed_data directory
        """
        if seed_data_path is None:
            # Default to seed_data in project root
            project_root = Path(__file__).parent.parent.parent
            seed_data_path = project_root / "seed_data"

        self.seed_data_path = Path(seed_data_path)
        self._cache = {}

    def load_bank_churners(self) -> List[Dict[str, Any]]:
        """
        Load bank customer churn data.

        Returns:
            list: List of customer records with 23 columns
        """
        if 'bank_churners' not in self._cache:
            self._cache['bank_churners'] = self._load_csv('BankChurners.csv')
        return self._cache['bank_churners']

    def load_customer_profiles(self) -> List[Dict[str, Any]]:
        """
        Load customer financial profiles.

        Returns:
            list: List of customer profiles with transactions
        """
        if 'customer_profiles' not in self._cache:
            self._cache['customer_profiles'] = self._load_csv('Customer_financial_profiles.csv')
        return self._cache['customer_profiles']

    def load_transactions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load large transaction dataset.

        Args:
            limit: Maximum number of records to load (None = all)

        Returns:
            list: List of transaction records
        """
        key = f'transactions_{limit}' if limit else 'transactions_all'

        if key not in self._cache:
            self._cache[key] = self._load_csv('bs140513_032310.csv', limit=limit)

        return self._cache[key]

    def load_net_transactions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load NET transaction dataset.

        Args:
            limit: Maximum number of records to load

        Returns:
            list: List of transaction records
        """
        key = f'net_transactions_{limit}' if limit else 'net_transactions_all'

        if key not in self._cache:
            self._cache[key] = self._load_csv('bsNET140513_032310.csv', limit=limit)

        return self._cache[key]

    def load_clustered_transactions(self) -> List[Dict[str, Any]]:
        """
        Load clustered transaction data.

        Returns:
            list: List of clustered transactions
        """
        if 'clustered_transactions' not in self._cache:
            self._cache['clustered_transactions'] = self._load_csv('clustered_transactions.csv')
        return self._cache['clustered_transactions']

    def get_sample_transactions(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get a random sample of transactions.

        Args:
            count: Number of transactions to return

        Returns:
            list: Random sample of transactions
        """
        # Load a reasonable chunk
        all_transactions = self.load_transactions(limit=10000)

        if len(all_transactions) <= count:
            return all_transactions

        return random.sample(all_transactions, count)

    def get_sample_customers(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get a random sample of customer profiles.

        Args:
            count: Number of customers to return

        Returns:
            list: Random sample of customers
        """
        all_customers = self.load_bank_churners()

        if len(all_customers) <= count:
            return all_customers

        return random.sample(all_customers, count)

    def generate_large_transaction_dataset(
        self,
        num_records: int,
        num_columns: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a large transaction dataset by sampling and augmenting seed data.

        Args:
            num_records: Number of records to generate
            num_columns: Number of columns to include (None = all)

        Returns:
            list: Large dataset of transactions
        """
        # Load seed transactions
        seed_data = self.load_transactions(limit=50000)

        if not seed_data:
            return []

        # Get all available columns
        all_columns = list(seed_data[0].keys()) if seed_data else []

        # Select columns if specified
        if num_columns and num_columns < len(all_columns):
            selected_columns = random.sample(all_columns, num_columns)
        else:
            selected_columns = all_columns

        # Generate dataset by sampling with replacement and slight variations
        large_dataset = []

        for i in range(num_records):
            # Pick a random seed record
            base_record = random.choice(seed_data)

            # Create new record with selected columns
            new_record = {}
            for col in selected_columns:
                if col in base_record:
                    value = base_record[col]

                    # Add slight variation to numeric values
                    if col in ['amount', 'step']:
                        try:
                            numeric_val = float(value)
                            # Add ±10% variation
                            variation = random.uniform(-0.1, 0.1)
                            new_value = numeric_val * (1 + variation)
                            new_record[col] = round(new_value, 2)
                        except (ValueError, TypeError):
                            new_record[col] = value
                    else:
                        new_record[col] = value

            large_dataset.append(new_record)

        return large_dataset

    def _load_csv(self, filename: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load a CSV file from seed_data directory.

        Args:
            filename: Name of CSV file
            limit: Maximum number of records to load

        Returns:
            list: List of dictionaries, one per row
        """
        filepath = self.seed_data_path / filename

        if not filepath.exists():
            print(f"Warning: Seed data file not found: {filepath}")
            return []

        data = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break
                    data.append(row)

        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []

        return data

    def get_available_datasets(self) -> List[str]:
        """
        Get list of available seed datasets.

        Returns:
            list: List of dataset names
        """
        if not self.seed_data_path.exists():
            return []

        csv_files = list(self.seed_data_path.glob('*.csv'))
        return [f.stem for f in csv_files]


# Global instance for easy access
_global_loader = None


def get_seed_loader() -> SeedDataLoader:
    """
    Get global seed data loader instance.

    Returns:
        SeedDataLoader: Global loader instance
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = SeedDataLoader()
    return _global_loader
