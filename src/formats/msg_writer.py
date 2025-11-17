"""
MSG and EML format writers for email messages.

Generates Outlook MSG and standard EML format emails.
"""

import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from datetime import datetime
from typing import Dict, Any
import os

from src.utils.watermark import get_watermark_html


class EMLWriter:
    """
    Writes emails to EML format (standard email format).
    """

    def __init__(self, filepath: str):
        """
        Initialize EML writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath

    def write(self, content: Dict[str, Any], doc_type: str = 'email'):
        """
        Write email content to EML file.

        Args:
            content: Email content dictionary
            doc_type: Type of document (always 'email' for this writer)

        Returns:
            str: Path to created file
        """
        # Create message
        msg = MIMEMultipart('alternative')

        # Set headers
        msg['From'] = f"{content['from']['name']} <{content['from']['email']}>"
        msg['To'] = f"{content['to']['name']} <{content['to']['email']}>"
        msg['Subject'] = content['subject']
        msg['Date'] = formatdate(localtime=True)

        # Add CC and BCC if present
        if content.get('cc'):
            msg['Cc'] = ', '.join([f"{c['name']} <{c['email']}>" for c in content['cc']])
        if content.get('bcc'):
            msg['Bcc'] = ', '.join([f"{c['name']} <{c['email']}>" for c in content['bcc']])

        # Priority
        if content.get('priority') == 'high':
            msg['X-Priority'] = '1'
            msg['Importance'] = 'high'

        # Body parts
        # Plain text with watermark
        text_body = get_watermark_html().replace('<div', '\n').replace('</div>', '\n').replace('<br/>', '\n')
        text_body = text_body.replace('<', '').replace('>', '')  # Strip HTML
        text_body += '\n\n' + content.get('body_text', '')

        # HTML with watermark
        html_body = get_watermark_html() + '\n' + content.get('body_html', content.get('body_text', ''))

        # Attach parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')

        msg.attach(part1)
        msg.attach(part2)

        # Write to file
        with open(self.filepath, 'w') as f:
            f.write(msg.as_string())

        return self.filepath


class MSGWriter:
    """
    Writes emails to MSG format (Outlook format).

    Note: This is a simplified implementation. For full MSG support,
    consider using a library like msglite or generating via pywin32 on Windows.
    For cross-platform compatibility, this creates a basic MSG structure using olefile.
    """

    def __init__(self, filepath: str):
        """
        Initialize MSG writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath

    def write(self, content: Dict[str, Any], doc_type: str = 'email'):
        """
        Write email content to MSG file.

        For simplicity and cross-platform compatibility, we'll create
        an EML file with .msg extension. Real MSG format requires
        complex OLE structures.

        For production use, consider using:
        - pywin32 on Windows
        - msg-extractor / msglite libraries
        - Or convert from EML using external tools

        Args:
            content: Email content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        # For now, create as EML but save as .msg
        # This will work in many email clients that can read EML
        eml_writer = EMLWriter(self.filepath)
        eml_writer.write(content, doc_type)

        return self.filepath


class EmailWriter:
    """
    Unified email writer that can output both MSG and EML formats.
    """

    def __init__(self, filepath: str):
        """
        Initialize email writer.

        Args:
            filepath: Output file path
        """
        self.filepath = filepath

    def write(self, content: Dict[str, Any], doc_type: str = 'email'):
        """
        Write email to appropriate format based on file extension.

        Args:
            content: Email content dictionary
            doc_type: Type of document

        Returns:
            str: Path to created file
        """
        _, ext = os.path.splitext(self.filepath)

        if ext.lower() == '.eml':
            writer = EMLWriter(self.filepath)
        elif ext.lower() == '.msg':
            writer = MSGWriter(self.filepath)
        else:
            # Default to EML
            writer = EMLWriter(self.filepath)

        return writer.write(content, doc_type)
