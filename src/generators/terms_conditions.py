"""
Terms and Conditions document generator.

Generates realistic legal-style terms and conditions documents
for payment processing and banking services.
"""

import random
from datetime import datetime
from typing import Dict, Any
from src.generators.base import BaseDocumentGenerator
from src.data.templates import DocumentTemplates


class TermsAndConditionsGenerator(BaseDocumentGenerator):
    """
    Generates Terms and Conditions documents.
    """

    def get_document_type(self) -> str:
        return 'terms_and_conditions'

    def get_supported_formats(self) -> list:
        return ['pdf', 'docx', 'odt']

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate a Terms and Conditions document.

        Returns:
            dict: Complete T&C document data
        """
        bank_name = self.data_generator.generate_bank_name()

        # Number of sections based on complexity (more sections = longer document)
        if 'num_pages_min' in self.config and 'num_pages_max' in self.config:
            # Roughly 1-2 sections per page
            num_sections = random.randint(
                self.config['num_pages_min'] * 1,
                self.config['num_pages_max'] * 2
            )
        else:
            num_sections = self.config.get('num_sections', random.randint(8, 12))

        # Generate sections
        sections = DocumentTemplates.generate_terms_and_conditions(
            bank_name=bank_name,
            num_sections=num_sections
        )

        # Document metadata
        effective_date = datetime.now()
        version = f"v{random.randint(1,5)}.{random.randint(0,9)}"

        content = {
            'title': f'{bank_name} Payment Services - Terms and Conditions',
            'bank_name': bank_name,
            'effective_date': effective_date,
            'version': version,
            'sections': sections,
            'footer': {
                'document_id': f'TC-{datetime.now().year}-{random.randint(1000, 9999)}',
                'last_updated': effective_date,
                'contact_email': f'legal@{bank_name.lower().replace(" ", "")}.com',
                'contact_phone': '1-800-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
            }
        }

        return content

    def estimate_content_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate metrics for size calculation.

        Args:
            content: T&C content

        Returns:
            dict: Metrics for size estimation
        """
        sections = content['sections']

        # Calculate total text length
        total_chars = len(content['title']) + 100  # Title and metadata

        for section in sections:
            total_chars += len(section['title'])
            total_chars += len(section['content'])

        # Estimate pages (approximately 500 words = 3000 chars per page)
        num_pages = max(1, total_chars // 3000)

        # Estimate paragraphs
        num_paragraphs = len(sections) * 3  # ~3 paragraphs per section

        return {
            'num_pages': num_pages,
            'total_chars': total_chars,
            'num_paragraphs': num_paragraphs,
        }
