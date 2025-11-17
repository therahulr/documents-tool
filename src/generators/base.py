"""
Base generator class for all document generators.

This module provides the abstract base class that all document generators
must inherit from, ensuring consistent interface and functionality.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List
from src.data.synthetic import SyntheticDataGenerator


class BaseDocumentGenerator(ABC):
    """
    Abstract base class for all document generators.

    All document generators must inherit from this class and implement
    the required methods.
    """

    def __init__(self, config: Dict[str, Any] = None, seed: int = None):
        """
        Initialize the document generator.

        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config or {}
        self.data_generator = SyntheticDataGenerator(seed=seed)
        self.seed = seed

    @abstractmethod
    def generate_content(self) -> Dict[str, Any]:
        """
        Generate the document content.

        This method must be implemented by subclasses to generate
        the actual document data structure.

        Returns:
            dict: Document content as a dictionary
        """
        pass

    @abstractmethod
    def get_document_type(self) -> str:
        """
        Get the document type identifier.

        Returns:
            str: Document type (e.g., 'bank_statement', 'credit_card_statement')
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported output formats for this document type.

        Returns:
            list: List of format extensions (e.g., ['pdf', 'docx', 'xlsx'])
        """
        # Default: most formats support these
        return ['pdf', 'docx']

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics from content for size estimation.

        Args:
            content: Document content dictionary

        Returns:
            dict: Metrics for size estimation (pages, chars, rows, etc.)
        """
        # Default implementation - subclasses can override
        return {
            'num_pages': content.get('num_pages', 1),
            'total_chars': len(str(content)),
        }

    def get_default_filename(self) -> str:
        """
        Get default filename for this document.

        Returns:
            str: Filename without extension
        """
        doc_type = self.get_document_type()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{doc_type}_{timestamp}"

    def validate_config(self) -> bool:
        """
        Validate the configuration.

        Returns:
            bool: True if config is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Base implementation - subclasses can add specific validation
        return True


class StatementGenerator(BaseDocumentGenerator):
    """
    Base class for statement-type documents (bank, credit card, etc.).
    """

    def __init__(self, config: Dict[str, Any] = None, seed: int = None):
        super().__init__(config, seed)

        # Generate customer profile (reused across document)
        person = self.data_generator.generate_person()
        address = self.data_generator.generate_address()

        self.customer = {
            **person,
            **address,
        }

        self.bank_name = self.data_generator.generate_bank_name()
        self.account_number = self.data_generator.generate_account_number()

    def get_supported_formats(self) -> List[str]:
        """Statements can be in most formats."""
        return ['pdf', 'docx', 'xlsx', 'odt', 'jpeg', 'png']


class LetterGenerator(BaseDocumentGenerator):
    """
    Base class for letter/notification documents.
    """

    def __init__(self, config: Dict[str, Any] = None, seed: int = None):
        super().__init__(config, seed)

        # Generate customer profile
        person = self.data_generator.generate_person()
        address = self.data_generator.generate_address()

        self.customer = {
            **person,
            **address,
        }

        self.bank_name = self.data_generator.generate_bank_name()

    def get_supported_formats(self) -> List[str]:
        """Letters can be documents or PDFs."""
        return ['pdf', 'docx', 'odt']


class EmailGenerator(BaseDocumentGenerator):
    """
    Base class for email documents.
    """

    def get_supported_formats(self) -> List[str]:
        """Emails are MSG or EML."""
        return ['msg', 'eml']

    def get_document_type(self) -> str:
        return 'email'
