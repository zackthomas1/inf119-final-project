"""
Test suite for syntax validation in CoderAgent and TesterAgent.
"""

import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import validate_python_syntax
from agents.coder_agent import CoderAgent
from agents.tester_agent import TesterAgent
from mcp_client import MCPClient

class TestSyntaxValidation(unittest.TestCase):
    """Test the utility function for syntax validation"""

    def test_validate_python_syntax_valid(self):
        """Test that valid Python code passes validation"""
        code = 'def hello():\n    print("Hello World")'
        is_valid, msg = validate_python_syntax(code)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "Valid syntax")

    def test_validate_python_syntax_invalid(self):
        """Test that invalid Python code fails validation"""
        code = 'def hello()\n    print("Hello World")'  # Missing colon
        is_valid, msg = validate_python_syntax(code)
        self.assertFalse(is_valid)
        self.assertIn("SyntaxError", msg)

class TestCoderAgentValidation(unittest.TestCase):
    """Test syntax validation and retry logic in CoderAgent"""

    def setUp(self):
        self.mock_mcp_client = MagicMock(spec=MCPClient)
        self.coder_agent = CoderAgent(self.mock_mcp_client)

    def test_generate_code_valid_first_try(self):
        """Test that valid code is returned immediately"""
        valid_code = "def main(): pass"
        self.mock_mcp_client.call_model.return_value = valid_code
        
        result = self.coder_agent.generate_code("requirements", {"raw_plan": "plan"})
        
        self.assertEqual(result, valid_code)
        self.assertEqual(self.mock_mcp_client.call_model.call_count, 1)

    def test_generate_code_retry_success(self):
        """Test that agent retries and succeeds after invalid syntax"""
        invalid_code = "def main() pass" # Syntax error
        valid_code = "def main(): pass"
        
        # First call returns invalid, second returns valid
        self.mock_mcp_client.call_model.side_effect = [invalid_code, valid_code]
        
        result = self.coder_agent.generate_code("requirements", {"raw_plan": "plan"})
        
        self.assertEqual(result, valid_code)
        self.assertEqual(self.mock_mcp_client.call_model.call_count, 2)
        
        # Verify the second call included the error message
        second_call_args = self.mock_mcp_client.call_model.call_args_list[1]
        messages = second_call_args[0][1] # args[1] is messages
        self.assertEqual(len(messages), 4) # system, user, assistant(invalid), user(error)
        self.assertIn("SyntaxError", messages[-1]["content"])

    def test_generate_code_retry_failure(self):
        """Test that agent gives up after max retries"""
        invalid_code = "def main() pass"
        self.mock_mcp_client.call_model.return_value = invalid_code
        
        result = self.coder_agent.generate_code("requirements", {"raw_plan": "plan"})
        
        self.assertEqual(result, invalid_code)
        self.assertEqual(self.mock_mcp_client.call_model.call_count, 3) # Max retries

class TestTesterAgentValidation(unittest.TestCase):
    """Test syntax validation and retry logic in TesterAgent"""

    def setUp(self):
        self.mock_mcp_client = MagicMock(spec=MCPClient)
        self.tester_agent = TesterAgent(self.mock_mcp_client)

    def test_generate_tests_retry_success(self):
        """Test that agent retries and succeeds after invalid syntax"""
        invalid_code = "def test_foo() assert True" # Syntax error
        valid_code = "def test_foo(): assert True"
        
        self.mock_mcp_client.call_model.side_effect = [invalid_code, valid_code]
        
        result = self.tester_agent.generate_tests("requirements", "code")
        
        self.assertEqual(result, valid_code)
        self.assertEqual(self.mock_mcp_client.call_model.call_count, 2)

if __name__ == '__main__':
    unittest.main()
