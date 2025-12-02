"""
File: utils.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: Contains utility functions for the application, including markdown stripping from LLM responses, Python syntax validation, and a helper to run generated tests using pytest.
"""

import re
import ast
import subprocess
import sys

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

def run_generated_tests(test_file_path: str = "generated/test_generated_app.py") -> tuple[bool, str]:
    """
    Runs the generated tests using pytest.
    Returns (True, output) if tests pass, (False, output) if they fail.
    """
    try:
        # Run pytest as a subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file_path],
            capture_output=True,
            text=True,
            timeout=30  # Timeout to prevent infinite loops in tests
        )
        
        # Combine stdout and stderr
        output = result.stdout + result.stderr
        
        # Return True if exit code is 0 (all tests passed)
        return result.returncode == 0, output
        
    except subprocess.TimeoutExpired:
        return False, "Tests timed out after 30 seconds."
    except Exception as e:
        return False, f"Failed to run tests: {str(e)}"
