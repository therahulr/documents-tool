"""
Format writers module.

This module contains all format-specific writers for generating documents.
"""

from .pdf_writer import PDFWriter
from .docx_writer import DOCXWriter
from .xlsx_writer import XLSXWriter
from .msg_writer import EmailWriter, EMLWriter, MSGWriter
from .odt_writer import ODTWriter
from .image_writer import ImageWriter

# Writer registry for easy lookup by file extension
WRITER_REGISTRY = {
    'pdf': PDFWriter,
    'docx': DOCXWriter,
    'xlsx': XLSXWriter,
    'msg': EmailWriter,
    'eml': EmailWriter,
    'odt': ODTWriter,
    'jpeg': ImageWriter,
    'jpg': ImageWriter,
    'png': ImageWriter,
}

# Supported formats for each document type
DOCUMENT_FORMAT_SUPPORT = {
    'bank_statement': ['pdf', 'docx', 'xlsx', 'odt', 'jpeg', 'jpg', 'png'],
    'credit_card_statement': ['pdf', 'docx', 'xlsx', 'odt', 'jpeg', 'jpg', 'png'],
    'terms_conditions': ['pdf', 'docx', 'odt'],
    'notification': ['pdf', 'docx', 'odt', 'jpeg', 'jpg', 'png'],
    'payment_advice': ['pdf', 'docx', 'xlsx', 'odt'],
    'email': ['msg', 'eml'],
}


def get_writer(filepath: str):
    """
    Get a writer instance based on file extension.

    Args:
        filepath: Output file path

    Returns:
        Writer instance

    Raises:
        ValueError: If file extension is not supported
    """
    ext = filepath.rsplit('.', 1)[-1].lower()

    if ext not in WRITER_REGISTRY:
        raise ValueError(f"Unsupported file format: {ext}")

    writer_class = WRITER_REGISTRY[ext]
    return writer_class(filepath)


def is_format_supported(doc_type: str, format_ext: str) -> bool:
    """
    Check if a format is supported for a document type.

    Args:
        doc_type: Document type
        format_ext: Format extension (e.g., 'pdf', 'docx')

    Returns:
        bool: True if supported
    """
    supported = DOCUMENT_FORMAT_SUPPORT.get(doc_type, [])
    return format_ext.lower() in supported


__all__ = [
    'PDFWriter',
    'DOCXWriter',
    'XLSXWriter',
    'EmailWriter',
    'EMLWriter',
    'MSGWriter',
    'ODTWriter',
    'ImageWriter',
    'WRITER_REGISTRY',
    'DOCUMENT_FORMAT_SUPPORT',
    'get_writer',
    'is_format_supported',
]
