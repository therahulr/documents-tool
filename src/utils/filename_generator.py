"""
Realistic document name generator.

Generates professional, realistic document filenames for synthetic documents.
"""

import random
from datetime import datetime
from typing import Optional


class DocumentNameGenerator:
    """
    Generates realistic document filenames.
    """

    # Company name components
    COMPANY_PREFIXES = [
        "Global", "United", "First", "Pacific", "Atlantic", "Northern", "Southern",
        "Eastern", "Western", "Central", "National", "International", "Continental",
        "Metropolitan", "Regional", "Premier", "Summit", "Apex", "Pinnacle", "Elite",
        "Prime", "Superior", "Advanced", "Modern", "Progressive", "Dynamic", "Strategic",
        "Integrated", "Consolidated", "Allied", "Associated", "Federal", "Universal",
        "Paramount", "Optimal", "Maximum", "Supreme", "Ultimate", "Dominant", "Leading"
    ]

    COMPANY_MIDDLES = [
        "Tech", "Financial", "Capital", "Ventures", "Industries", "Corporation",
        "Enterprises", "Systems", "Solutions", "Services", "Partners", "Group",
        "Holdings", "Banking", "Investment", "Asset", "Wealth", "Trust", "Management",
        "Advisory", "Consulting", "Analytics", "Data", "Digital", "Cloud", "Cyber",
        "Software", "Hardware", "Network", "Security", "Innovation", "Research"
    ]

    COMPANY_SUFFIXES = [
        "Corp", "Inc", "LLC", "Ltd", "Co", "Group", "Partners", "Associates",
        "Holdings", "Capital", "Ventures", "Enterprises", "Systems", "Solutions"
    ]

    # Document type names
    FINANCE_DOCS = [
        "Statement", "Report", "Summary", "Analysis", "Overview", "Review",
        "Forecast", "Projection", "Budget", "Ledger", "Balance_Sheet",
        "Income_Statement", "Cash_Flow", "Financial_Report", "Annual_Report",
        "Quarterly_Report", "Monthly_Statement", "Transaction_Record",
        "Account_Summary", "Portfolio_Analysis", "Investment_Report",
        "Credit_Report", "Loan_Statement", "Mortgage_Document",
        "Tax_Document", "Audit_Report", "Compliance_Report"
    ]

    DATA_DOCS = [
        "Dataset", "Data_Export", "Transaction_Data", "Customer_Data",
        "Sales_Data", "Revenue_Data", "Analytics_Report", "Metrics_Report",
        "Performance_Data", "Historical_Data", "Master_Data", "Raw_Data",
        "Processed_Data", "Aggregated_Data", "Detailed_Records"
    ]

    VISUAL_DOCS = [
        "Chart", "Graph", "Visualization", "Dashboard", "Infographic",
        "Diagram", "Analytics_Visual", "Performance_Chart", "Trend_Analysis",
        "Comparison_Chart", "Financial_Chart", "Revenue_Graph",
        "Growth_Chart", "Distribution_Chart", "Heat_Map"
    ]

    LEGAL_DOCS = [
        "Agreement", "Contract", "Terms_And_Conditions", "Privacy_Policy",
        "Service_Agreement", "License_Agreement", "NDA", "MOU",
        "Partnership_Agreement", "Vendor_Agreement", "Client_Agreement",
        "Master_Agreement", "Addendum", "Amendment", "Disclosure",
        "Consent_Form", "Authorization", "Waiver", "Release"
    ]

    COMMUNICATION_DOCS = [
        "Notification", "Notice", "Letter", "Memo", "Correspondence",
        "Update", "Alert", "Bulletin", "Announcement", "Communication",
        "Advisory", "Reminder", "Confirmation", "Acknowledgment"
    ]

    RESEARCH_DOCS = [
        "Research_Paper", "White_Paper", "Technical_Document",
        "Case_Study", "Analysis_Report", "Market_Research", "Study",
        "Investigation", "Survey_Results", "Findings", "Conclusion",
        "Methodology", "Documentation", "Specification", "Guidelines"
    ]

    # Descriptive adjectives
    ADJECTIVES = [
        "Comprehensive", "Detailed", "Annual", "Quarterly", "Monthly",
        "Weekly", "Daily", "Final", "Preliminary", "Draft", "Revised",
        "Updated", "Complete", "Partial", "Summary", "Executive",
        "Confidential", "Internal", "External", "Official", "Certified",
        "Verified", "Audited", "Approved", "Consolidated", "Combined"
    ]

    # Time periods
    TIME_PERIODS = [
        "2024", "2023", "Q1", "Q2", "Q3", "Q4", "FY2024", "FY2023",
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        "H1", "H2", "YTD", "MTD", "YE", "EOY"
    ]

    @classmethod
    def generate_company_name(cls, num_parts: int = None) -> str:
        """
        Generate a realistic company name.

        Args:
            num_parts: Number of name parts (1-3), None for random

        Returns:
            str: Company name like "Global_Tech_Solutions" or "Pacific_Financial_Corp"
        """
        if num_parts is None:
            num_parts = random.randint(2, 3)

        parts = []

        # Always include prefix
        parts.append(random.choice(cls.COMPANY_PREFIXES))

        if num_parts >= 2:
            parts.append(random.choice(cls.COMPANY_MIDDLES))

        if num_parts >= 3:
            parts.append(random.choice(cls.COMPANY_SUFFIXES))

        return "_".join(parts)

    @classmethod
    def generate_filename(
        cls,
        doc_type: str,
        file_format: str,
        include_company: bool = True,
        include_adjective: bool = None,
        include_time: bool = None,
        include_test_marker: bool = None
    ) -> str:
        """
        Generate a realistic document filename.

        Args:
            doc_type: Type of document (bank_statement, credit_card, etc.)
            file_format: File extension (pdf, xlsx, etc.)
            include_company: Include company name
            include_adjective: Include descriptive adjective (None = random)
            include_time: Include time period (None = random)
            include_test_marker: Include '_test' suffix (None = random)

        Returns:
            str: Realistic filename
        """
        parts = []

        # Randomly decide optional inclusions if not specified
        if include_adjective is None:
            include_adjective = random.random() < 0.3  # 30% chance

        if include_time is None:
            include_time = random.random() < 0.4  # 40% chance

        if include_test_marker is None:
            include_test_marker = random.random() < 0.2  # 20% chance

        # Company name
        if include_company:
            parts.append(cls.generate_company_name())

        # Adjective
        if include_adjective:
            parts.append(random.choice(cls.ADJECTIVES))

        # Document type specific name
        doc_name = cls._get_document_type_name(doc_type)
        parts.append(doc_name)

        # Time period
        if include_time:
            parts.append(random.choice(cls.TIME_PERIODS))

        # Random unique suffix (2-3 digits)
        suffix_digits = random.randint(2, 3)
        unique_suffix = ''.join([str(random.randint(0, 9)) for _ in range(suffix_digits)])
        parts.append(unique_suffix)

        # Test marker
        if include_test_marker:
            parts.append("test")

        # Join and add extension
        filename = "_".join(parts) + "." + file_format.lower()

        return filename

    @classmethod
    def _get_document_type_name(cls, doc_type: str) -> str:
        """
        Get a realistic name for a document type.

        Args:
            doc_type: Internal document type

        Returns:
            str: Realistic document name
        """
        mappings = {
            'bank_statement': cls.FINANCE_DOCS,
            'credit_card_statement': cls.FINANCE_DOCS,
            'payment_advice': cls.FINANCE_DOCS,
            'terms_conditions': cls.LEGAL_DOCS,
            'notification': cls.COMMUNICATION_DOCS,
            'email': cls.COMMUNICATION_DOCS,
            'research_paper': cls.RESEARCH_DOCS,
            'annual_report': cls.FINANCE_DOCS,
            'data_export': cls.DATA_DOCS,
        }

        # Get appropriate category or default to finance
        category = mappings.get(doc_type, cls.FINANCE_DOCS)

        # For image formats, prefer visual docs
        return random.choice(category)

    @classmethod
    def generate_batch_filenames(
        cls,
        doc_type: str,
        file_format: str,
        count: int
    ) -> list:
        """
        Generate a batch of unique filenames.

        Args:
            doc_type: Document type
            file_format: File extension
            count: Number of filenames to generate

        Returns:
            list: List of unique filenames
        """
        filenames = set()

        while len(filenames) < count:
            filename = cls.generate_filename(doc_type, file_format)
            filenames.add(filename)

        return list(filenames)


# Convenience function
def generate_realistic_filename(doc_type: str, file_format: str) -> str:
    """
    Quick function to generate a realistic filename.

    Args:
        doc_type: Document type
        file_format: File extension

    Returns:
        str: Realistic filename
    """
    return DocumentNameGenerator.generate_filename(doc_type, file_format)
