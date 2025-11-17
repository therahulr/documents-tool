"""
Document generators module.

This module contains all document type generators.
"""

from src.generators.bank_statement import BankStatementGenerator
from src.generators.credit_card_statement import CreditCardStatementGenerator
from src.generators.terms_conditions import TermsAndConditionsGenerator
from src.generators.notification import NotificationGenerator
from src.generators.payment_advice import PaymentAdviceGenerator
from src.generators.email import EmailGenerator

# Generator registry for easy lookup
GENERATOR_REGISTRY = {
    'bank_statement': BankStatementGenerator,
    'credit_card_statement': CreditCardStatementGenerator,
    'terms_conditions': TermsAndConditionsGenerator,
    'notification': NotificationGenerator,
    'payment_advice': PaymentAdviceGenerator,
    'email': EmailGenerator,
}

# Human-readable names for CLI
GENERATOR_NAMES = {
    'bank_statement': 'Bank Statement',
    'credit_card_statement': 'Credit Card Statement',
    'terms_conditions': 'Terms & Conditions / Agreement',
    'notification': 'Notification / Letter',
    'payment_advice': 'Payment / Remittance Advice',
    'email': 'Email (.msg)',
}


def get_generator(doc_type: str, config: dict = None, seed: int = None):
    """
    Get a generator instance by document type.

    Args:
        doc_type: Document type key
        config: Configuration dictionary
        seed: Random seed for reproducibility

    Returns:
        BaseDocumentGenerator: Generator instance

    Raises:
        ValueError: If document type is not recognized
    """
    if doc_type not in GENERATOR_REGISTRY:
        raise ValueError(f"Unknown document type: {doc_type}")

    generator_class = GENERATOR_REGISTRY[doc_type]
    return generator_class(config=config, seed=seed)


__all__ = [
    'BankStatementGenerator',
    'CreditCardStatementGenerator',
    'TermsAndConditionsGenerator',
    'NotificationGenerator',
    'PaymentAdviceGenerator',
    'EmailGenerator',
    'GENERATOR_REGISTRY',
    'GENERATOR_NAMES',
    'get_generator',
]
