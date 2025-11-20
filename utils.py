"""
File: utils.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [
]
"""

import re

def strip_markdown_formatting(text: str) -> str:
    """
    Remove markdown code block formatting from generated code.
    Strips ```python, ```, and similar markdown code fences.
    
    Args:
        text: Raw text that may contain markdown formatting
        
    Returns:
        Cleaned text with markdown formatting removed
    """
    if not text or not isinstance(text, str):
        return text
    
    # Remove opening code fences (```python, ```py, ```, etc.)
    text = re.sub(r'^\s*```\w*\s*\n?', '', text, flags=re.MULTILINE)
    
    # Remove closing code fences
    text = re.sub(r'\n?\s*```\s*$', '', text, flags=re.MULTILINE | re.DOTALL)
    
    # Remove any remaining standalone ``` lines
    text = re.sub(r'^\s*```\s*$', '', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace at the beginning and end
    text = text.strip()
    
    return text
