"""
Utility functions for DEADLINEAI application.

This module provides helper functions for common operations used throughout
the application, including date/time handling, formatting, and data validation.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import re


def get_current_utc_time() -> str:
    """
    Get the current UTC time in formatted string.
    
    Returns:
        str: Current UTC time in 'YYYY-MM-DD HH:MM:SS' format
    """
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def format_datetime(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format a datetime object to a string.
    
    Args:
        dt (datetime): The datetime object to format
        fmt (str): The format string (default: 'YYYY-MM-DD HH:MM:SS')
    
    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(fmt)


def parse_datetime(date_string: str, fmt: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    Parse a datetime string to a datetime object.
    
    Args:
        date_string (str): The date string to parse
        fmt (str): The format of the input string
    
    Returns:
        Optional[datetime]: Parsed datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_string, fmt)
    except ValueError:
        return None


def validate_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email (str): The email address to validate
    
    Returns:
        bool: True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text (str): The text to truncate
        max_length (int): Maximum length of the result (default: 100)
        suffix (str): Suffix to add if truncated (default: '...')
    
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def remove_duplicates(items: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.
    
    Args:
        items (List[Any]): List that may contain duplicates
    
    Returns:
        List[Any]: List with duplicates removed
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries into a single dictionary.
    
    Args:
        *dicts: Variable number of dictionaries to merge
    
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with a default fallback.
    
    Args:
        data (Dict[str, Any]): The dictionary to search
        key (str): The key to retrieve
        default (Any): Default value if key not found
    
    Returns:
        Any: The value at the key or the default value
    """
    return data.get(key, default)


def is_valid_url(url: str) -> bool:
    """
    Validate a URL format.
    
    Args:
        url (str): The URL to validate
    
    Returns:
        bool: True if URL format is valid, False otherwise
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


if __name__ == '__main__':
    # Example usage
    print(f"Current UTC Time: {get_current_utc_time()}")
    print(f"Valid email test: {validate_email('user@example.com')}")
    print(f"Truncated text: {truncate_string('This is a very long string that needs to be truncated', 30)}")
