"""
File: test_mcp_client.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [What this file does (functions/methods used)]
"""

"""
Test suite for MCPClient integration with Google Gemini API.
Tests both successful API calls and error handling scenarios.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import MCPClient
from model_tracker import UsageTracker


class TestMCPClientGeminiIntegration(unittest.TestCase):
    """Test cases for MCP Client with Google Gemini API"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.usage_tracker = UsageTracker()
        
    def test_initialization_with_api_key(self):
        """Test that MCPClient initializes correctly with API key"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
            with patch('google.generativeai.configure') as mock_configure:
                client = MCPClient(self.usage_tracker)
                mock_configure.assert_called_once_with(api_key='test-api-key')
                self.assertIsInstance(client.usage_tracker, UsageTracker)

    def test_initialization_without_api_key(self):
        """Test that MCPClient raises error when API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                MCPClient(self.usage_tracker)
            self.assertIn("GEMINI_API_KEY environment variable not set", str(context.exception))

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_single_message_call(self, mock_model_class, mock_configure):
        """Test API call with single message"""
        # Mock setup
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Hello! How can I help you today?"
        mock_model.generate_content.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
            client = MCPClient(self.usage_tracker)
            
            messages = [{"role": "user", "content": "Hello, how are you?"}]
            result = client.call_model("test_agent", "gemini-2.0-flash", messages)
            
            # Assertions
            self.assertEqual(result, "Hello! How can I help you today?")
            mock_model_class.assert_called_once_with("gemini-2.0-flash")
            mock_model.generate_content.assert_called_once_with("Hello, how are you?")
            
            # Check usage tracking
            usage_data = self.usage_tracker.to_dict()
            self.assertIn("test_agent", usage_data)
            self.assertEqual(usage_data["test_agent"]["numApiCalls"], 1)
            self.assertGreater(usage_data["test_agent"]["totalTokens"], 0)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_multi_message_conversation(self, mock_model_class, mock_configure):
        """Test API call with multi-turn conversation"""
        # Mock setup
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "I understand your question about Python."
        mock_model.generate_content.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
            client = MCPClient(self.usage_tracker)
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is Python?"},
                {"role": "assistant", "content": "Python is a programming language."},
                {"role": "user", "content": "Tell me more about it."}
            ]
            result = client.call_model("test_agent", "gemini-2.0-flash", messages)
            
            expected_prompt = (
                "System: You are a helpful assistant.\n"
                "User: What is Python?\n"
                "Assistant: Python is a programming language.\n"
                "User: Tell me more about it."
            )
            
            # Assertions
            self.assertEqual(result, "I understand your question about Python.")
            mock_model.generate_content.assert_called_once_with(expected_prompt)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_api_call_error_handling(self, mock_model_class, mock_configure):
        """Test error handling when API call fails"""
        # Mock setup
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("API rate limit exceeded")
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
            client = MCPClient(self.usage_tracker)
            
            messages = [{"role": "user", "content": "Hello"}]
            
            with self.assertRaises(Exception) as context:
                client.call_model("test_agent", "gemini-2.0-flash", messages)
            
            self.assertIn("API rate limit exceeded", str(context.exception))

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_empty_message_handling(self, mock_model_class, mock_configure):
        """Test handling of empty or malformed messages"""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "I see an empty message."
        mock_model.generate_content.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
            client = MCPClient(self.usage_tracker)
            
            # Test with empty content
            messages = [{"role": "user", "content": ""}]
            result = client.call_model("test_agent", "gemini-2.0-flash", messages)
            
            self.assertEqual(result, "I see an empty message.")
            mock_model.generate_content.assert_called_once_with("")

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_usage_tracking_multiple_calls(self, mock_model_class, mock_configure):
        """Test that usage tracking works correctly across multiple calls"""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
            client = MCPClient(self.usage_tracker)
            
            # Make multiple calls
            messages = [{"role": "user", "content": "Test message"}]
            client.call_model("agent_1", "gemini-2.0-flash", messages)
            client.call_model("agent_1", "gemini-2.0-flash", messages)
            client.call_model("agent_2", "gemini-2.5-flash", messages)
            
            usage_data = self.usage_tracker.to_dict()
            
            # Check that both agents are tracked
            self.assertIn("agent_1", usage_data)
            self.assertIn("agent_2", usage_data)
            
            # agent_1 should have 2 calls
            self.assertEqual(usage_data["agent_1"]["numApiCalls"], 2)
            
            # agent_2 should have 1 call
            self.assertEqual(usage_data["agent_2"]["numApiCalls"], 1)


class TestMCPClientIntegrationWithRealAPI(unittest.TestCase):
    """Integration tests with real Gemini API (requires valid API key)"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.usage_tracker = UsageTracker()
        self.api_key = os.getenv('GEMINI_API_KEY')
        
    @unittest.skipIf(not os.getenv('GEMINI_API_KEY'), "GEMINI_API_KEY not set")
    def test_real_api_call(self):
        """Test actual API call to Gemini (only runs if API key is available)"""
        client = MCPClient(self.usage_tracker)
        
        messages = [{"role": "user", "content": "Say 'Hello, World!' and nothing else."}]
        
        try:
            result = client.call_model("test_agent", "gemini-2.0-flash", messages)
            
            # Basic checks
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            # Should contain the expected response
            self.assertIn("Hello, World!", result)
            
            # Check usage tracking
            usage_data = self.usage_tracker.to_dict()
            self.assertIn("test_agent", usage_data)
            self.assertEqual(usage_data["test_agent"]["numApiCalls"], 1)
            self.assertGreater(usage_data["test_agent"]["totalTokens"], 0)
            
            print(f"SUCCESS: Real API call completed. Response: {result}")
            print(f"Usage stats: {usage_data}")
            
        except Exception as e:
            self.fail(f"Real API call failed: {e}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
