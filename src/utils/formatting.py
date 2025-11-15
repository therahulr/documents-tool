"""
Formatting utilities for consistent data presentation across documents.
"""

from datetime import datetime
from typing import Union


def format_currency(amount: Union[float, int], symbol: str = "$") -> str:
    """
    Format a number as USD currency.

    Args:
        amount: The numeric amount
        symbol: Currency symbol (default: $)

    Returns:
        str: Formatted currency string (e.g., "$1,234.56")
    """
    # Handle negative amounts
    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    return f"{symbol}{amount:,.2f}"


def format_date(date: datetime, format_str: str = "%m/%d/%Y") -> str:
    """
    Format a datetime object as a string.

    Args:
        date: The datetime object
        format_str: Format string (default: MM/DD/YYYY - US style)

    Returns:
        str: Formatted date string
    """
    return date.strftime(format_str)


def format_date_long(date: datetime) -> str:
    """
    Format a datetime object in long format.

    Args:
        date: The datetime object

    Returns:
        str: Formatted date string (e.g., "January 15, 2024")
    """
    return date.strftime("%B %d, %Y")


def format_datetime(dt: datetime, format_str: str = "%m/%d/%Y %I:%M %p") -> str:
    """
    Format a datetime object with time.

    Args:
        dt: The datetime object
        format_str: Format string (default: MM/DD/YYYY HH:MM AM/PM)

    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)


def format_account_number(account_num: str, mask: bool = False) -> str:
    """
    Format an account number with proper spacing/grouping.

    Args:
        account_num: The account number
        mask: Whether to mask the number (show only last 4 digits)

    Returns:
        str: Formatted account number
    """
    if mask and len(account_num) > 4:
        return f"****{account_num[-4:]}"

    # Add spacing every 4 digits
    return " ".join([account_num[i:i+4] for i in range(0, len(account_num), 4)])


def format_card_number(card_num: str, mask: bool = True) -> str:
    """
    Format a credit card number.

    Args:
        card_num: The card number (16 digits)
        mask: Whether to mask the number (show only last 4 digits)

    Returns:
        str: Formatted card number (e.g., "**** **** **** 1234")
    """
    if mask:
        if len(card_num) >= 4:
            return f"**** **** **** {card_num[-4:]}"
        return card_num

    # Group by 4
    return " ".join([card_num[i:i+4] for i in range(0, len(card_num), 4)])


def format_phone(phone: str) -> str:
    """
    Format a phone number in US format.

    Args:
        phone: The phone number (10 digits)

    Returns:
        str: Formatted phone number (e.g., "(555) 123-4567")
    """
    # Remove non-digits
    digits = ''.join(c for c in phone if c.isdigit())

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return as-is if format doesn't match


def format_routing_number(routing: str) -> str:
    """
    Format a routing number (9 digits) with spacing.

    Args:
        routing: The routing number

    Returns:
        str: Formatted routing number (e.g., "123-456-789")
    """
    if len(routing) == 9:
        return f"{routing[:3]}-{routing[3:6]}-{routing[6:]}"
    return routing


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a number as a percentage.

    Args:
        value: The decimal value (e.g., 0.15 for 15%)
        decimals: Number of decimal places

    Returns:
        str: Formatted percentage (e.g., "15.00%")
    """
    return f"{value * 100:.{decimals}f}%"


def format_address_block(street: str, city: str, state: str, zip_code: str) -> str:
    """
    Format an address as a multi-line block.

    Args:
        street: Street address
        city: City name
        state: State abbreviation
        zip_code: ZIP code

    Returns:
        str: Formatted address block
    """
    return f"{street}\n{city}, {state} {zip_code}"


def format_address_inline(street: str, city: str, state: str, zip_code: str) -> str:
    """
    Format an address as a single line.

    Args:
        street: Street address
        city: City name
        state: State abbreviation
        zip_code: ZIP code

    Returns:
        str: Formatted address inline
    """
    return f"{street}, {city}, {state} {zip_code}"
