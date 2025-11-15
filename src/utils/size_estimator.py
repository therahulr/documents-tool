"""
File size estimation utilities.

These utilities help estimate the approximate file size of documents
based on their content, allowing for size-based generation control.
"""

from typing import Dict, Any


class SizeEstimator:
    """
    Estimates file sizes for different document formats based on content.

    These are empirical estimates and may not be perfectly accurate,
    but should be within ±20% for most cases.
    """

    # Base overhead for each format (bytes)
    BASE_SIZES = {
        'pdf': 5000,      # PDF header, metadata, fonts
        'docx': 15000,    # XML structure, relationships, styles
        'xlsx': 8000,     # Workbook structure, styles, sheets
        'msg': 10000,     # MSG file structure, headers
        'eml': 2000,      # Email headers
        'odt': 12000,     # ODF XML structure
        'jpeg': 1000,     # JPEG headers
        'png': 1000,      # PNG headers
    }

    # Bytes per content unit
    CONTENT_COSTS = {
        'pdf': {
            'page': 2000,           # Base cost per page
            'char': 0.5,            # Cost per character
            'table_row': 100,       # Cost per table row
            'image_kb': 1024,       # Cost per KB of image
        },
        'docx': {
            'paragraph': 200,       # Cost per paragraph
            'char': 0.8,            # Cost per character
            'table_row': 150,       # Cost per table row
            'image_kb': 1024,       # Cost per KB of image
        },
        'xlsx': {
            'row': 50,              # Cost per row
            'cell': 20,             # Cost per cell
            'char': 1.0,            # Cost per character in cell
            'style': 200,           # Cost per unique style
        },
        'msg': {
            'char': 1.0,            # Cost per character in body
            'attachment_kb': 1024,  # Cost per KB of attachment
            'header': 100,          # Cost per header field
        },
        'eml': {
            'char': 1.0,            # Cost per character in body
            'attachment_kb': 1024,  # Cost per KB of attachment
            'header': 50,           # Cost per header field
        },
        'odt': {
            'paragraph': 250,       # Cost per paragraph
            'char': 1.0,            # Cost per character
            'table_row': 180,       # Cost per table row
        },
        'jpeg': {
            'pixel': 0.25,          # Rough estimate with compression
        },
        'png': {
            'pixel': 0.5,           # Less compression than JPEG
        },
    }

    @classmethod
    def estimate_pdf_size(cls, content: Dict[str, Any]) -> int:
        """
        Estimate PDF file size.

        Args:
            content: Dictionary with keys:
                - num_pages: Number of pages
                - total_chars: Total character count
                - num_table_rows: Number of table rows
                - image_size_kb: Total size of images in KB

        Returns:
            int: Estimated size in bytes
        """
        costs = cls.CONTENT_COSTS['pdf']
        base = cls.BASE_SIZES['pdf']

        size = base
        size += content.get('num_pages', 1) * costs['page']
        size += content.get('total_chars', 0) * costs['char']
        size += content.get('num_table_rows', 0) * costs['table_row']
        size += content.get('image_size_kb', 0) * costs['image_kb']

        return int(size)

    @classmethod
    def estimate_docx_size(cls, content: Dict[str, Any]) -> int:
        """
        Estimate DOCX file size.

        Args:
            content: Dictionary with keys:
                - num_paragraphs: Number of paragraphs
                - total_chars: Total character count
                - num_table_rows: Number of table rows
                - image_size_kb: Total size of images in KB

        Returns:
            int: Estimated size in bytes
        """
        costs = cls.CONTENT_COSTS['docx']
        base = cls.BASE_SIZES['docx']

        size = base
        size += content.get('num_paragraphs', 0) * costs['paragraph']
        size += content.get('total_chars', 0) * costs['char']
        size += content.get('num_table_rows', 0) * costs['table_row']
        size += content.get('image_size_kb', 0) * costs['image_kb']

        return int(size)

    @classmethod
    def estimate_xlsx_size(cls, content: Dict[str, Any]) -> int:
        """
        Estimate XLSX file size.

        Args:
            content: Dictionary with keys:
                - num_rows: Number of rows
                - num_cols: Number of columns
                - total_chars: Total character count
                - num_styles: Number of unique styles

        Returns:
            int: Estimated size in bytes
        """
        costs = cls.CONTENT_COSTS['xlsx']
        base = cls.BASE_SIZES['xlsx']

        num_rows = content.get('num_rows', 0)
        num_cols = content.get('num_cols', 0)

        size = base
        size += num_rows * costs['row']
        size += (num_rows * num_cols) * costs['cell']
        size += content.get('total_chars', 0) * costs['char']
        size += content.get('num_styles', 5) * costs['style']

        return int(size)

    @classmethod
    def estimate_msg_size(cls, content: Dict[str, Any]) -> int:
        """
        Estimate MSG file size.

        Args:
            content: Dictionary with keys:
                - body_chars: Character count in body
                - num_headers: Number of header fields
                - attachment_size_kb: Total attachment size in KB

        Returns:
            int: Estimated size in bytes
        """
        costs = cls.CONTENT_COSTS['msg']
        base = cls.BASE_SIZES['msg']

        size = base
        size += content.get('body_chars', 0) * costs['char']
        size += content.get('num_headers', 5) * costs['header']
        size += content.get('attachment_size_kb', 0) * costs['attachment_kb']

        return int(size)

    @classmethod
    def estimate_eml_size(cls, content: Dict[str, Any]) -> int:
        """
        Estimate EML file size.

        Args:
            content: Dictionary with keys:
                - body_chars: Character count in body
                - num_headers: Number of header fields
                - attachment_size_kb: Total attachment size in KB

        Returns:
            int: Estimated size in bytes
        """
        costs = cls.CONTENT_COSTS['eml']
        base = cls.BASE_SIZES['eml']

        size = base
        size += content.get('body_chars', 0) * costs['char']
        size += content.get('num_headers', 5) * costs['header']
        size += content.get('attachment_size_kb', 0) * costs['attachment_kb']

        return int(size)

    @classmethod
    def estimate_odt_size(cls, content: Dict[str, Any]) -> int:
        """
        Estimate ODT file size.

        Args:
            content: Dictionary with keys:
                - num_paragraphs: Number of paragraphs
                - total_chars: Total character count
                - num_table_rows: Number of table rows

        Returns:
            int: Estimated size in bytes
        """
        costs = cls.CONTENT_COSTS['odt']
        base = cls.BASE_SIZES['odt']

        size = base
        size += content.get('num_paragraphs', 0) * costs['paragraph']
        size += content.get('total_chars', 0) * costs['char']
        size += content.get('num_table_rows', 0) * costs['table_row']

        return int(size)

    @classmethod
    def estimate_image_size(cls, width: int, height: int, format_type: str = 'jpeg') -> int:
        """
        Estimate image file size.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            format_type: 'jpeg' or 'png'

        Returns:
            int: Estimated size in bytes
        """
        format_type = format_type.lower()
        if format_type not in ['jpeg', 'png']:
            format_type = 'jpeg'

        costs = cls.CONTENT_COSTS[format_type]
        base = cls.BASE_SIZES[format_type]

        total_pixels = width * height
        size = base + (total_pixels * costs['pixel'])

        return int(size)

    @classmethod
    def format_size(cls, size_bytes: int) -> str:
        """
        Format a byte size as human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            str: Formatted size (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    @classmethod
    def parse_size_string(cls, size_str: str) -> int:
        """
        Parse a size string to bytes.

        Args:
            size_str: Size string (e.g., "10MB", "1.5 GB", "500 KB")

        Returns:
            int: Size in bytes
        """
        size_str = size_str.strip().upper()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
        }

        # Extract number and unit
        import re
        match = re.match(r'([\d.]+)\s*([KMGT]?B)', size_str)
        if not match:
            raise ValueError(f"Invalid size string: {size_str}")

        value = float(match.group(1))
        unit = match.group(2)

        return int(value * multipliers[unit])
