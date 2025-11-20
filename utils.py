
import re
import ast

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

def validate_python_syntax(code: str) -> tuple[bool, str]:
    """
    Checks if the provided code string has valid Python syntax.
    Returns (True, "Valid syntax") or (False, error_message).
    """
    try:
        ast.parse(code)
        return True, "Valid syntax"
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Validation Error: {str(e)}"
